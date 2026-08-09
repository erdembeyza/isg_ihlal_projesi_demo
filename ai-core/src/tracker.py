"""
Basit IoU tabanlı geçici kişi takibi (kimlik tanıma yok).

Amaç: aynı siluet kareler boyunca izlenip ihlal süresi biriktirilsin;
eşik aşılınca backend'e bildirilsin. Aynı tip için global cooldown ile
video döngüsünde / kısa aralıklı tekrar kayıtlar engellenir.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def kutu_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    kesisim = iw * ih
    if kesisim <= 0:
        return 0.0
    alan_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    alan_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    birlesim = alan_a + alan_b - kesisim
    return kesisim / birlesim if birlesim > 0 else 0.0


@dataclass
class AktifTrack:
    track_id: int
    kutu: tuple[int, int, int, int]
    son_gorulme: float
    ihlal_sureleri: dict[str, float] = field(default_factory=dict)
    bildirilen_tipler: set[str] = field(default_factory=set)
    son_guven: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class BildirilecekIhlal:
    track_id: int
    ihlal_tipi_adi: str
    sure_saniye: int
    guven: float
    kisi_kutusu: tuple[int, int, int, int]


class IoUTracker:
    def __init__(
        self,
        *,
        iou_esigi: float = 0.25,
        kayip_tolerans_saniye: float = 6.0,
        min_sure_saniye: float = 8.0,
        yeniden_bildirim_saniye: float = 120.0,
    ) -> None:
        self._iou_esigi = iou_esigi
        self._kayip_tolerans = kayip_tolerans_saniye
        self._min_sure = min_sure_saniye
        self._yeniden_bildirim = max(1.0, yeniden_bildirim_saniye)
        self._sonraki_id = 1
        self._trackler: dict[int, AktifTrack] = {}
        # Tip bazinda kamera geneli cooldown (track olumunde bile spam olmaz).
        self._son_global_bildirim: dict[str, float] = {}

    def devam_et(self, dt: float, simdi: float) -> list[BildirilecekIhlal]:
        """YOLO atlanan karelerde mevcut ihlal surelerini gercek zamanla ilerlet."""
        if dt <= 0 or not self._trackler:
            return []
        for track in self._trackler.values():
            for tip in list(track.ihlal_sureleri.keys()):
                if tip in track.bildirilen_tipler:
                    continue
                if self._cooldown_aktif(tip, simdi):
                    continue
                track.ihlal_sureleri[tip] = track.ihlal_sureleri.get(tip, 0.0) + dt
        return self._esik_kontrolu(simdi, kaybolanlari_temizle=False)

    def guncelle(
        self,
        ihlaller: list,
        simdi: float,
        dt: float,
    ) -> list[BildirilecekIhlal]:
        kutular: dict[tuple[int, int, int, int], list] = {}
        for ihlal in ihlaller:
            kutular.setdefault(ihlal.kisi_kutusu, []).append(ihlal)

        eslesmeyen_track_idler = set(self._trackler.keys())
        kullanilan_kutular: set[tuple[int, int, int, int]] = set()

        adaylar: list[tuple[float, int, tuple[int, int, int, int]]] = []
        for tid, track in self._trackler.items():
            for kutu in kutular:
                skor = kutu_iou(track.kutu, kutu)
                if skor >= self._iou_esigi:
                    adaylar.append((skor, tid, kutu))
        adaylar.sort(reverse=True)

        for _, tid, kutu in adaylar:
            if tid not in eslesmeyen_track_idler or kutu in kullanilan_kutular:
                continue
            track = self._trackler[tid]
            track.kutu = kutu
            track.son_gorulme = simdi
            eslesmeyen_track_idler.discard(tid)
            kullanilan_kutular.add(kutu)
            self._sure_biriktir(track, kutular[kutu], simdi, dt)

        for kutu, grup in kutular.items():
            if kutu in kullanilan_kutular:
                continue
            tid = self._sonraki_id
            self._sonraki_id += 1
            track = AktifTrack(track_id=tid, kutu=kutu, son_gorulme=simdi)
            self._trackler[tid] = track
            self._sure_biriktir(track, grup, simdi, dt)

        return self._esik_kontrolu(simdi, kaybolanlari_temizle=True, eslesmeyen=eslesmeyen_track_idler)

    def _cooldown_aktif(self, tip: str, simdi: float) -> bool:
        son = self._son_global_bildirim.get(tip)
        return son is not None and (simdi - son) < self._yeniden_bildirim

    def _esik_kontrolu(
        self,
        simdi: float,
        *,
        kaybolanlari_temizle: bool,
        eslesmeyen: set[int] | None = None,
    ) -> list[BildirilecekIhlal]:
        bildirilecek: list[BildirilecekIhlal] = []

        for track in self._trackler.values():
            for tip, sure in list(track.ihlal_sureleri.items()):
                if tip in track.bildirilen_tipler:
                    continue
                if self._cooldown_aktif(tip, simdi):
                    # Yeni track olsabile cooldown varken sure sifirla; spam birikmesin.
                    track.ihlal_sureleri[tip] = 0.0
                    continue
                if sure >= self._min_sure:
                    self._bildirimi_isaretle(track, tip, simdi)
                    bildirilecek.append(
                        BildirilecekIhlal(
                            track_id=track.track_id,
                            ihlal_tipi_adi=tip,
                            sure_saniye=int(sure),
                            guven=track.son_guven.get(tip, 0.0),
                            kisi_kutusu=track.kutu,
                        )
                    )

        if kaybolanlari_temizle and eslesmeyen is not None:
            silinecek: list[int] = []
            for tid in eslesmeyen:
                track = self._trackler[tid]
                if simdi - track.son_gorulme < self._kayip_tolerans:
                    continue
                for tip, sure in track.ihlal_sureleri.items():
                    if tip in track.bildirilen_tipler:
                        continue
                    if self._cooldown_aktif(tip, simdi):
                        continue
                    if sure >= self._min_sure:
                        self._bildirimi_isaretle(track, tip, simdi)
                        bildirilecek.append(
                            BildirilecekIhlal(
                                track_id=track.track_id,
                                ihlal_tipi_adi=tip,
                                sure_saniye=int(sure),
                                guven=track.son_guven.get(tip, 0.0),
                                kisi_kutusu=track.kutu,
                            )
                        )
                silinecek.append(tid)
            for tid in silinecek:
                self._trackler.pop(tid, None)

        return bildirilecek

    def _bildirimi_isaretle(self, track: AktifTrack, tip: str, simdi: float) -> None:
        track.bildirilen_tipler.add(tip)
        self._son_global_bildirim[tip] = simdi

    def _sure_biriktir(self, track: AktifTrack, ihlaller: list, simdi: float, dt: float) -> None:
        if dt <= 0:
            return
        for ihlal in ihlaller:
            tip = ihlal.ihlal_tipi_adi
            if tip in track.bildirilen_tipler or self._cooldown_aktif(tip, simdi):
                track.son_guven[tip] = ihlal.guven
                continue
            track.ihlal_sureleri[tip] = track.ihlal_sureleri.get(tip, 0.0) + dt
            track.son_guven[tip] = ihlal.guven
