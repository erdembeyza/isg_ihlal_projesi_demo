"""
MODUL-1 (tasarim_mimari.md): AI Core ana orkestrasyon dongusu.

Guvenlik kamerasi (RTSP) veya yerel video okur, her N karede bir YOLO
cikarimi calistirir, IoU tracker ile ihlal suresi biriktirir; esik asilinca
kanit karesini backend'e bildirir. Periyodik kamera heartbeat gonderir.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from .backend_client import BackendIstemcisi
from .config import Ayarlar
from .face_blur import yuzleri_blurla
from .ppe_detector import Ihlal, PpeDedektoru, kisi_cizim_kutusunu_genislet
from .stream import akisi_surdur, canli_akismi
from .tracker import IoUTracker, kutu_iou

logger = logging.getLogger(__name__)

GOSTERIM_PENCERE_ADI = "ISG Ihlal Tespiti - AI Core"
# OpenCV GUI cagrilari (imshow/waitKey) Windows'ta thread-safe degil.
_OPENCV_GUI_KILIDI = threading.Lock()


def ekran_boyutu() -> tuple[int, int]:
    try:
        import ctypes

        user32 = ctypes.windll.user32
        genislik = max(640, int(user32.GetSystemMetrics(0)))
        yukseklik = max(480, int(user32.GetSystemMetrics(1)))
        return genislik, yukseklik
    except Exception:
        return 1280, 720


def _ekran_boyutu() -> tuple[int, int]:
    """Geriye donuk; tek kamera gosteriminde biraz kenar payi birak."""
    w, h = ekran_boyutu()
    return max(640, int(w * 0.90)), max(480, int(h * 0.85))


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
        pencere_konum: tuple[int, int] | None = None,
        pencere_max_boyut: tuple[int, int] | None = None,
    ):
        self._ayarlar = ayarlar
        self._dedektor = dedektor or PpeDedektoru(ayarlar)
        self._backend = None if kuru_calistirma else (backend or BackendIstemcisi(ayarlar))
        self._kuru_calistirma = kuru_calistirma
        self._goster = goster
        self._debug_cikti_klasoru = debug_cikti_klasoru
        self._pencere_konum = pencere_konum
        self._bildirim_sayaci = 0
        self._kare_no = 0
        self._gosterim_penceresi_hazir = False
        if pencere_max_boyut is not None:
            self._gosterim_max_genislik, self._gosterim_max_yukseklik = pencere_max_boyut
        else:
            self._gosterim_max_genislik, self._gosterim_max_yukseklik = _ekran_boyutu()
        self._durdur = False
        self._tracker = IoUTracker(
            min_sure_saniye=ayarlar.ihlal_min_sure_saniye,
            yeniden_bildirim_saniye=ayarlar.detection_cooldown_saniye,
        )
        logger.info(
            "[%s] Kayit esikleri: min_sure=%.0fs, tekrar_kayit_cooldown=%.0fs",
            ayarlar.kamera_adi or f"bolge-{ayarlar.bolge_id}",
            ayarlar.ihlal_min_sure_saniye,
            ayarlar.detection_cooldown_saniye,
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
                # destroyAllWindows diger kameranin penceresini de kapatir.
                with _OPENCV_GUI_KILIDI:
                    try:
                        cv2.destroyWindow(self._gosterim_pencere_adi())
                    except cv2.error:
                        pass

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
            ihlal = self._kanit_icin_ihlal_hizala(kare, bildirim, ihlaller)
            if ihlal is None:
                logger.warning(
                    "[%s] Ihlal atlandi: karede eslesen kisi kutusu yok (tip=%s)",
                    self._ayarlar.kamera_adi or f"bolge-{self._ayarlar.bolge_id}",
                    bildirim.ihlal_tipi_adi,
                )
                continue
            self._ihlali_bildir(kare, ihlal, bildirim.sure_saniye)

        if self._goster:
            with _OPENCV_GUI_KILIDI:
                self._kareyi_ciz_ve_goster(kare, ihlaller)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info(
                        "[%s] Kullanici 'q' ile cikisi tetikledi.",
                        self._ayarlar.kamera_adi or f"bolge-{self._ayarlar.bolge_id}",
                    )
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

    def _guncel_kisi_kutusu(
        self,
        kare: np.ndarray,
        referans: tuple[int, int, int, int],
        *,
        min_iou: float = 0.08,
    ) -> tuple[int, int, int, int] | None:
        """Bu karedeki YOLO kisi kutularından referansa en cok ortuseni sec."""
        kisiler = self._dedektor.kisi_kutularini_bul(kare)
        if not kisiler:
            return None
        en_iyi = max(kisiler, key=lambda k: kutu_iou(referans, k))
        if kutu_iou(referans, en_iyi) >= min_iou:
            return en_iyi
        # IoU dusukse merkez mesafesiyle dene (kisi hizli hareket etmis olabilir)
        def merkez(k: tuple[int, int, int, int]) -> tuple[float, float]:
            return (k[0] + k[2]) / 2.0, (k[1] + k[3]) / 2.0

        rx, ry = merkez(referans)
        en_yakin = min(
            kisiler,
            key=lambda k: (merkez(k)[0] - rx) ** 2 + (merkez(k)[1] - ry) ** 2,
        )
        ex, ey = merkez(en_yakin)
        kosegen = max(
            1.0,
            ((en_yakin[2] - en_yakin[0]) ** 2 + (en_yakin[3] - en_yakin[1]) ** 2) ** 0.5,
        )
        if (((ex - rx) ** 2 + (ey - ry) ** 2) ** 0.5) / kosegen <= 0.6:
            return en_yakin
        return None

    def _kanit_icin_ihlal_hizala(
        self,
        kare: np.ndarray,
        bildirim,
        anlik_ihlaller: list[Ihlal],
    ) -> Ihlal | None:
        """
        Kirmizi cerceve icin bu karedeki GERCEK kisi kutusunu bulur.
        Kisi yoksa None (yanlis nesne kutusuna asla cizilmez/kaydedilmez).
        """
        guven = bildirim.guven
        referans = bildirim.kisi_kutusu

        # Ayni tip anlik ihlallerden kisi adayi (zaten kisiye bagli)
        adaylar = [
            i for i in anlik_ihlaller if i.ihlal_tipi_adi == bildirim.ihlal_tipi_adi
        ]
        if not adaylar:
            adaylar = [
                i
                for i in self._dedektor.tespit_et(kare)
                if i.ihlal_tipi_adi == bildirim.ihlal_tipi_adi
            ]
        if adaylar:
            en_iyi = max(adaylar, key=lambda i: kutu_iou(referans, i.kisi_kutusu))
            referans = en_iyi.kisi_kutusu
            guven = en_iyi.guven

        kisi = self._guncel_kisi_kutusu(kare, referans)
        if kisi is None:
            return None

        return Ihlal(
            ihlal_tipi_adi=bildirim.ihlal_tipi_adi,
            guven=guven,
            kisi_kutusu=kisi,
            cizim_kutusu=kisi_cizim_kutusunu_genislet(
                kisi, kare_boyutu=kare.shape[:2]
            ),
        )

    def _ihlali_bildir(self, kare: np.ndarray, ihlal: Ihlal, sure_saniye: int) -> None:
        tespit_zamani = datetime.now()
        # Yuz blur: yalnizca bu karedeki YOLO kisi kutulari.
        kisi_kutulari = self._dedektor.kisi_kutularini_bul(kare)
        if not kisi_kutulari:
            kisi_kutulari = [ihlal.kisi_kutusu]
        elif not any(kutu_iou(ihlal.kisi_kutusu, k) >= 0.08 for k in kisi_kutulari):
            kisi_kutulari = [*kisi_kutulari, ihlal.kisi_kutusu]
        kanit_kare = yuzleri_blurla(kare, kisi_kutulari)
        # Kirmizi cerceve: ihlal sahibi kisinin guncel kutusu.
        kanit_kare = self._ihlal_kutusunu_ciz(kanit_kare, ihlal)

        if self._kuru_calistirma:
            self._bildirim_sayaci += 1
            logger.info(
                "[KURU CALISTIRMA] Ihlal: tip=%s guven=%.2f sure=%ss kutu=%s "
                "(backend'e GONDERILMEDI)",
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
                sure_saniye,
                ihlal.kutu_cizim_icin(),
            )
            if self._debug_cikti_klasoru is not None:
                self._debug_ciktisini_kaydet(kanit_kare, ihlal, tespit_zamani)
            return

        try:
            sonuc = self._backend.ihlal_bildir(  # type: ignore[union-attr]
                ihlal.ihlal_tipi_adi,
                kanit_kare,
                tespit_zamani,
                bolge_id=self._ayarlar.bolge_id,
                sure_saniye=sure_saniye,
            )
            self._bildirim_sayaci += 1
            logger.info(
                "Ihlal backend'e bildirildi: id=%s tip=%s guven=%.2f sure=%ss "
                "bolge_id=%s bolge_kaynak=%s kamera=%s",
                sonuc.get("id"),
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
                sure_saniye,
                self._ayarlar.bolge_id,
                self._ayarlar.video_kaynagi,
                self._ayarlar.kamera_adi or "-",
            )
        except Exception:
            logger.exception(
                "Ihlal bildirimi basarisiz oldu (kamera=%s), bu tespit atlaniyor.",
                self._ayarlar.kamera_adi or "-",
            )

    def _debug_ciktisini_kaydet(self, kare, ihlal: Ihlal, zaman: datetime) -> None:
        self._debug_cikti_klasoru.mkdir(parents=True, exist_ok=True)
        damga = zaman.strftime("%Y%m%d_%H%M%S_%f")
        cv2.imwrite(str(self._debug_cikti_klasoru / f"{damga}_{ihlal.ihlal_tipi_adi}.jpg"), kare)

    @staticmethod
    def _cizim_koordinatlari(kare: np.ndarray, ihlal: Ihlal) -> tuple[int, int, int, int]:
        """Kafa payi eklenmis cerceve; cizim_kutusu varsa onu (kare sinirinda) kullan."""
        h, w = kare.shape[:2]
        if ihlal.cizim_kutusu is not None:
            x1, y1, x2, y2 = ihlal.cizim_kutusu
            return max(0, x1), max(0, y1), min(w - 1, x2), min(h - 1, y2)
        return kisi_cizim_kutusunu_genislet(ihlal.kisi_kutusu, kare_boyutu=(h, w))

    @classmethod
    def _ihlal_kutusunu_ciz(
        cls,
        kare: np.ndarray, ihlal: Ihlal, *, kopyala: bool = True
    ) -> np.ndarray:
        """--show ile ayni stil: kirmizi dikdortgen (kafa dahil genisletilmis) + etiket."""
        cizili = kare.copy() if kopyala else kare
        x1, y1, x2, y2 = cls._cizim_koordinatlari(cizili, ihlal)
        cv2.rectangle(cizili, (x1, y1), (x2, y2), (0, 0, 255), 2)
        etiket = f"{ihlal.ihlal_tipi_adi} {ihlal.guven:.2f}"
        cv2.putText(
            cizili, etiket, (x1, max(0, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2,
        )
        return cizili

    def _ihlal_karelerini_ciz(self, kare: np.ndarray, ihlaller: list[Ihlal]) -> np.ndarray:
        """Ihlal kutularini kareye cizer (ayri pencere acmaz)."""
        gosterilecek = kare.copy()
        cizilen: set[tuple[int, int, int, int]] = set()
        for ihlal in ihlaller:
            if ihlal.kisi_kutusu in cizilen:
                x1, y1, _, _ = self._cizim_koordinatlari(gosterilecek, ihlal)
                cv2.putText(
                    gosterilecek,
                    f"{ihlal.ihlal_tipi_adi} {ihlal.guven:.2f}",
                    (x1, max(0, y1 - 28)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2,
                )
                continue
            cizilen.add(ihlal.kisi_kutusu)
            self._ihlal_kutusunu_ciz(gosterilecek, ihlal, kopyala=False)
        return gosterilecek

    def _kareyi_ciz_ve_goster(self, kare: np.ndarray, ihlaller: list[Ihlal]) -> None:
        gosterilecek = self._ihlal_karelerini_ciz(kare, ihlaller)
        gosterilecek = _ekrana_sigdir(
            gosterilecek, self._gosterim_max_genislik, self._gosterim_max_yukseklik
        )

        pencere = self._gosterim_pencere_adi()

        if not self._gosterim_penceresi_hazir:
            cv2.namedWindow(pencere, cv2.WINDOW_NORMAL)
            h, w = gosterilecek.shape[:2]
            cv2.resizeWindow(pencere, w, h)
            if self._pencere_konum is not None:
                cv2.moveWindow(pencere, self._pencere_konum[0], self._pencere_konum[1])
            self._gosterim_penceresi_hazir = True

        cv2.imshow(pencere, gosterilecek)

    def _gosterim_pencere_adi(self) -> str:
        ad = GOSTERIM_PENCERE_ADI
        if self._ayarlar.kamera_adi:
            ad = f"{GOSTERIM_PENCERE_ADI} - {self._ayarlar.kamera_adi}"
        return ad.encode("ascii", "replace").decode("ascii")
