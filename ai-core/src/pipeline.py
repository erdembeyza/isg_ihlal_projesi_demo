"""
MODUL-1 (tasarim_mimari.md): AI Core ana orkestrasyon dongusu.

Guvenlik kamerasi (RTSP) veya yerel video okur, her N karede bir YOLO
cikarimi calistirir, ihlal tespit edildiginde (cooldown'a takilmadiysa)
kanit karesini backend'e bildirir.

Canli akista kopma olursa otomatik yeniden baglanir; surekli calisir.
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
        self._son_bildirim_zamani: dict[str, float] = {}
        self._bildirim_sayaci = 0
        self._kare_no = 0
        self._gosterim_penceresi_hazir = False
        self._gosterim_max_genislik, self._gosterim_max_yukseklik = _ekran_boyutu()
        self._durdur = False

    @property
    def bildirim_sayaci(self) -> int:
        return self._bildirim_sayaci

    def calistir(self, kaynak: str | None = None, dongu: bool = False) -> None:
        video_kaynagi = kaynak or self._ayarlar.video_kaynagi
        canli = canli_akismi(video_kaynagi)
        # Canli kamera: surekli. Dosya + --loop: canli simulasyonu.
        dongu_dosya = (not canli) and dongu
        etiket = self._ayarlar.kamera_adi or f"bolge-{self._ayarlar.bolge_id}"

        logger.info(
            "[%s] Kaynak baslatiliyor: %s (canli=%s, demo_modu=%s, kuru=%s, bolge_id=%s)",
            etiket,
            video_kaynagi,
            canli,
            self._dedektor.demo_modu_mu,
            self._kuru_calistirma,
            self._ayarlar.bolge_id,
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
        if self._kare_no % self._ayarlar.frame_atlama != 0:
            return True

        ihlaller = self._dedektor.tespit_et(kare)
        self._ihlalleri_isle(kare, ihlaller)

        if self._goster:
            self._kareyi_ciz_ve_goster(kare, ihlaller)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("Kullanici 'q' ile cikisi tetikledi.")
                self._durdur = True
                return False
        return True

    def _ihlalleri_isle(self, kare: np.ndarray, ihlaller: list[Ihlal]) -> None:
        simdi = time.monotonic()
        for ihlal in ihlaller:
            son_bildirim = self._son_bildirim_zamani.get(ihlal.ihlal_tipi_adi, 0.0)
            if simdi - son_bildirim < self._ayarlar.detection_cooldown_saniye:
                continue

            self._son_bildirim_zamani[ihlal.ihlal_tipi_adi] = simdi
            self._ihlali_bildir(kare, ihlal)

    def _ihlali_bildir(self, kare: np.ndarray, ihlal: Ihlal) -> None:
        tespit_zamani = datetime.now()

        if self._kuru_calistirma:
            self._bildirim_sayaci += 1
            logger.info(
                "[KURU CALISTIRMA] Ihlal: tip=%s guven=%.2f kutu=%s (backend'e GONDERILMEDI)",
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
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
            )
            self._bildirim_sayaci += 1
            logger.info(
                "Ihlal backend'e bildirildi: id=%s tip=%s guven=%.2f bolge_id=%s",
                sonuc.get("id"),
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
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
        """OpenCV Windows'ta Unicode pencere adlarini bozup ikinci bos pencere acabiliyor."""
        ad = GOSTERIM_PENCERE_ADI
        if self._ayarlar.kamera_adi:
            ad = f"{GOSTERIM_PENCERE_ADI} - {self._ayarlar.kamera_adi}"
        # ASCII'ye indir: em-dash / Turkce karakter kaynakli cift pencereyi onler.
        return ad.encode("ascii", "replace").decode("ascii")
