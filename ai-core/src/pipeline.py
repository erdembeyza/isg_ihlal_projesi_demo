"""
MODUL-1 (tasarim_mimari.md): AI Core ana orkestrasyon dongusu.

Guvenlik kamerasi (RTSP) veya yerel video okur, her N karede bir YOLO
cikarimi calistirir, IoU tracker ile ihlal suresi biriktirir; esik asilinca
kanit karesini backend'e bildirir. Periyodik kamera heartbeat gonderir.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from .backend_client import BackendIstemcisi
from .config import Ayarlar
from .ppe_detector import Ihlal, PpeDedektoru
from .stream import akisi_surdur, canli_akismi
from .tracker import IoUTracker

logger = logging.getLogger(__name__)

GOSTERIM_PENCERE_ADI = "ISG Ihlal Tespiti - AI Core"


def _ekran_boyutu() -> tuple[int, int]:
    try:
        import ctypes

        user32 = ctypes.windll.user32
        genislik = max(640, int(user32.GetSystemMetrics(0) * 0.90))
        yukseklik = max(480, int(user32.GetSystemMetrics(1) * 0.85))
        return genislik, yukseklik
    except Exception:
        return 1280, 720


def _ekrana_sigdir(kare: np.ndarray, max_genislik: int, max_yukseklik: int) -> np.ndarray:
    yukseklik, genislik = kare.shape[:2]
    if genislik <= 0 or yukseklik <= 0:
        return kare
    olcek = min(max_genislik / genislik, max_yukseklik / yukseklik, 1.0)
    if olcek >= 0.999:
        return kare
    yeni_w = max(1, int(genislik * olcek))
    yeni_h = max(1, int(yukseklik * olcek))
    return cv2.resize(kare, (yeni_w, yeni_h), interpolation=cv2.INTER_AREA)


class IhlalPipeline:
    def __init__(
        self,
        ayarlar: Ayarlar,
        dedektor: PpeDedektoru | None = None,
        backend: BackendIstemcisi | None = None,
        kuru_calistirma: bool = False,
        goster: bool = False,
        debug_cikti_klasoru: Path | None = None,
    ):
        self._ayarlar = ayarlar
        self._dedektor = dedektor or PpeDedektoru(ayarlar)
        self._backend = None if kuru_calistirma else (backend or BackendIstemcisi(ayarlar))
        self._kuru_calistirma = kuru_calistirma
        self._goster = goster
        self._debug_cikti_klasoru = debug_cikti_klasoru
        self._bildirim_sayaci = 0
        self._kare_no = 0
        self._gosterim_penceresi_hazir = False
        self._gosterim_max_genislik, self._gosterim_max_yukseklik = _ekran_boyutu()
        self._durdur = False
        self._tracker = IoUTracker(
            min_sure_saniye=ayarlar.ihlal_min_sure_saniye,
        )
        self._son_kare_zamani: float | None = None
        self._son_islem_zamani: float | None = None
        self._son_heartbeat = 0.0
        self._fps_kare_sayaci = 0
        self._fps_pencere_baslangic = time.monotonic()
        self._son_fps = 0.0

    @property
    def bildirim_sayaci(self) -> int:
        return self._bildirim_sayaci

    def calistir(self, kaynak: str | None = None, dongu: bool = False) -> None:
        video_kaynagi = kaynak or self._ayarlar.video_kaynagi
        canli = canli_akismi(video_kaynagi)
        dongu_dosya = (not canli) and dongu
        etiket = self._ayarlar.kamera_adi or f"bolge-{self._ayarlar.bolge_id}"

        logger.info(
            "[%s] Kaynak baslatiliyor: %s (canli=%s, demo_modu=%s, kuru=%s, "
            "bolge_id=%s, min_sure=%.0fs)",
            etiket,
            video_kaynagi,
            canli,
            self._dedektor.demo_modu_mu,
            self._kuru_calistirma,
            self._ayarlar.bolge_id,
            self._ayarlar.ihlal_min_sure_saniye,
        )

        try:
            akisi_surdur(
                video_kaynagi,
                canli=canli,
                dongu_dosya=dongu_dosya,
                buffer_size=self._ayarlar.stream_buffer_size,
                rtsp_tcp=self._ayarlar.stream_rtsp_tcp,
                yeniden_baglan_saniye=self._ayarlar.stream_yeniden_baglan_saniye,
                max_yeniden_baglanma=self._ayarlar.stream_max_yeniden_baglanma,
                kare_isle=self._kareyi_isle,
            )
        except KeyboardInterrupt:
            logger.info("[%s] Pipeline kullanici tarafindan durduruldu (Ctrl+C).", etiket)
        finally:
            if self._goster:
                cv2.destroyAllWindows()

    def _kareyi_isle(self, kare: np.ndarray) -> bool:
        if self._durdur:
            return False

        self._kare_no += 1
        self._fps_guncelle()
        self._heartbeat_gonder()

        simdi = time.monotonic()
        dt = 0.0 if self._son_kare_zamani is None else max(0.0, simdi - self._son_kare_zamani)
        self._son_kare_zamani = simdi

        ihlaller: list[Ihlal] = []
        # YOLO her N karede bir; sure biriktirme HER karede gercek zamanla devam eder.
        if self._kare_no % self._ayarlar.frame_atlama == 0:
            self._son_islem_zamani = simdi
            ihlaller = self._dedektor.tespit_et(kare)
            bildirilecekler = self._tracker.guncelle(ihlaller, simdi, dt)
        else:
            bildirilecekler = self._tracker.devam_et(dt, simdi)

        for bildirim in bildirilecekler:
            ihlal = Ihlal(
                ihlal_tipi_adi=bildirim.ihlal_tipi_adi,
                guven=bildirim.guven,
                kisi_kutusu=bildirim.kisi_kutusu,
            )
            self._ihlali_bildir(kare, ihlal, bildirim.sure_saniye)

        if self._goster:
            self._kareyi_ciz_ve_goster(kare, ihlaller)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("Kullanici 'q' ile cikisi tetikledi.")
                self._durdur = True
                return False
        return True

    def _fps_guncelle(self) -> None:
        self._fps_kare_sayaci += 1
        gecen = time.monotonic() - self._fps_pencere_baslangic
        if gecen >= 1.0:
            self._son_fps = self._fps_kare_sayaci / gecen
            self._fps_kare_sayaci = 0
            self._fps_pencere_baslangic = time.monotonic()

    def _heartbeat_gonder(self) -> None:
        if self._kuru_calistirma or self._backend is None:
            return
        simdi = time.monotonic()
        if simdi - self._son_heartbeat < self._ayarlar.heartbeat_saniye:
            return
        self._son_heartbeat = simdi
        kamera_adi = self._ayarlar.kamera_adi or f"bolge-{self._ayarlar.bolge_id}"
        try:
            self._backend.kamera_heartbeat(
                bolge_id=self._ayarlar.bolge_id,
                kamera_adi=kamera_adi,
                fps=round(self._son_fps, 1),
                son_kare_zamani=datetime.now(),
            )
        except Exception:
            logger.debug("Kamera heartbeat gonderilemedi", exc_info=True)

    def _ihlali_bildir(self, kare: np.ndarray, ihlal: Ihlal, sure_saniye: int) -> None:
        tespit_zamani = datetime.now()

        if self._kuru_calistirma:
            self._bildirim_sayaci += 1
            logger.info(
                "[KURU CALISTIRMA] Ihlal: tip=%s guven=%.2f sure=%ss kutu=%s "
                "(backend'e GONDERILMEDI)",
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
                sure_saniye,
                ihlal.kisi_kutusu,
            )
            if self._debug_cikti_klasoru is not None:
                self._debug_ciktisini_kaydet(kare, ihlal, tespit_zamani)
            return

        try:
            sonuc = self._backend.ihlal_bildir(  # type: ignore[union-attr]
                ihlal.ihlal_tipi_adi,
                kare,
                tespit_zamani,
                bolge_id=self._ayarlar.bolge_id,
                sure_saniye=sure_saniye,
            )
            self._bildirim_sayaci += 1
            logger.info(
                "Ihlal backend'e bildirildi: id=%s tip=%s guven=%.2f sure=%ss bolge_id=%s",
                sonuc.get("id"),
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
                sure_saniye,
                self._ayarlar.bolge_id,
            )
        except Exception:
            logger.exception("Ihlal bildirimi basarisiz oldu, bu tespit atlaniyor.")

    def _debug_ciktisini_kaydet(self, kare, ihlal: Ihlal, zaman: datetime) -> None:
        self._debug_cikti_klasoru.mkdir(parents=True, exist_ok=True)
        damga = zaman.strftime("%Y%m%d_%H%M%S_%f")
        cv2.imwrite(str(self._debug_cikti_klasoru / f"{damga}_{ihlal.ihlal_tipi_adi}.jpg"), kare)

    def _kareyi_ciz_ve_goster(self, kare: np.ndarray, ihlaller: list[Ihlal]) -> None:
        gosterilecek = kare.copy()
        for ihlal in ihlaller:
            x1, y1, x2, y2 = ihlal.kisi_kutusu
            cv2.rectangle(gosterilecek, (x1, y1), (x2, y2), (0, 0, 255), 2)
            etiket = f"{ihlal.ihlal_tipi_adi} {ihlal.guven:.2f}"
            cv2.putText(
                gosterilecek, etiket, (x1, max(0, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2,
            )

        gosterilecek = _ekrana_sigdir(
            gosterilecek, self._gosterim_max_genislik, self._gosterim_max_yukseklik
        )

        pencere = self._gosterim_pencere_adi()

        if not self._gosterim_penceresi_hazir:
            cv2.namedWindow(pencere, cv2.WINDOW_NORMAL)
            h, w = gosterilecek.shape[:2]
            cv2.resizeWindow(pencere, w, h)
            self._gosterim_penceresi_hazir = True

        cv2.imshow(pencere, gosterilecek)

    def _gosterim_pencere_adi(self) -> str:
        ad = GOSTERIM_PENCERE_ADI
        if self._ayarlar.kamera_adi:
            ad = f"{GOSTERIM_PENCERE_ADI} - {self._ayarlar.kamera_adi}"
        return ad.encode("ascii", "replace").decode("ascii")
