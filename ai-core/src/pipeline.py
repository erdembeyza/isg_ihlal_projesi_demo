"""
MODUL-1 (tasarim_mimari.md): AI Core ana orkestrasyon dongusu.

Video kaynagini (RTSP akisi veya yerel dosya) okur, her N karede bir YOLO
cikarimi calistirir, ihlal tespit edildiginde (cooldown'a takilmadiysa)
kanit karesini yuz-blurlu kopyasiyla birlikte backend'e bildirir.
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
from .face_blur import kisi_yuzunu_blurla
from .ppe_detector import Ihlal, PpeDedektoru

logger = logging.getLogger(__name__)


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

    @property
    def bildirim_sayaci(self) -> int:
        return self._bildirim_sayaci

    def calistir(self, kaynak: str | None = None, dongu: bool = False) -> None:
        video_kaynagi = kaynak or self._ayarlar.video_kaynagi
        logger.info(
            "Video kaynagi aciliyor: %s (demo_modu=%s, kuru_calistirma=%s)",
            video_kaynagi,
            self._dedektor.demo_modu_mu,
            self._kuru_calistirma,
        )

        yakalayici = cv2.VideoCapture(video_kaynagi)
        if not yakalayici.isOpened():
            raise RuntimeError(f"Video kaynagi acilamadi: {video_kaynagi}")

        kare_no = 0
        try:
            while True:
                basarili, kare = yakalayici.read()
                if not basarili:
                    if dongu:
                        yakalayici.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    logger.info("Video kaynagi bitti, pipeline durduruluyor.")
                    break

                kare_no += 1
                if kare_no % self._ayarlar.frame_atlama != 0:
                    continue

                ihlaller = self._dedektor.tespit_et(kare)
                self._ihlalleri_isle(kare, ihlaller)

                if self._goster:
                    self._kareyi_ciz_ve_goster(kare, ihlaller)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        logger.info("Kullanici 'q' ile cikisi tetikledi.")
                        break
        except KeyboardInterrupt:
            logger.info("Pipeline kullanici tarafindan durduruldu (Ctrl+C).")
        finally:
            yakalayici.release()
            if self._goster:
                cv2.destroyAllWindows()

    def _ihlalleri_isle(self, kare: np.ndarray, ihlaller: list[Ihlal]) -> None:
        # Ayni karede ayni ihlal tipinden birden fazla varsa (ör. iki kisi
        # baretsiz), bildirim basina bir kez islenir; hepsi icin ayri ayri
        # cooldown/POST yapilir (her biri ayri bir kanit karesidir degil,
        # ayni kare ama farkli kisi kutusu -> farkli blur alani).
        simdi = time.monotonic()
        for ihlal in ihlaller:
            son_bildirim = self._son_bildirim_zamani.get(ihlal.ihlal_tipi_adi, 0.0)
            if simdi - son_bildirim < self._ayarlar.detection_cooldown_saniye:
                continue

            self._son_bildirim_zamani[ihlal.ihlal_tipi_adi] = simdi
            self._ihlali_bildir(kare, ihlal)

    def _ihlali_bildir(self, kare: np.ndarray, ihlal: Ihlal) -> None:
        orijinal = kare
        blurlu = kisi_yuzunu_blurla(kare, ihlal.kisi_kutusu)
        tespit_zamani = datetime.now()

        if self._kuru_calistirma:
            self._bildirim_sayaci += 1
            logger.info(
                "[KURU CALISTIRMA] Ihlal tespit edildi: tip=%s guven=%.2f kutu=%s "
                "(backend'e GONDERILMEDI)",
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
                ihlal.kisi_kutusu,
            )
            if self._debug_cikti_klasoru is not None:
                self._debug_ciktisini_kaydet(orijinal, blurlu, ihlal, tespit_zamani)
            return

        try:
            sonuc = self._backend.ihlal_bildir(  # type: ignore[union-attr]
                ihlal.ihlal_tipi_adi, orijinal, blurlu, tespit_zamani
            )
            self._bildirim_sayaci += 1
            logger.info(
                "Ihlal backend'e bildirildi: id=%s tip=%s guven=%.2f",
                sonuc.get("id"),
                ihlal.ihlal_tipi_adi,
                ihlal.guven,
            )
        except Exception:
            logger.exception("Ihlal bildirimi basarisiz oldu, bu tespit atlaniyor.")

    def _debug_ciktisini_kaydet(self, orijinal, blurlu, ihlal: Ihlal, zaman: datetime) -> None:
        self._debug_cikti_klasoru.mkdir(parents=True, exist_ok=True)
        damga = zaman.strftime("%Y%m%d_%H%M%S_%f")
        cv2.imwrite(str(self._debug_cikti_klasoru / f"{damga}_{ihlal.ihlal_tipi_adi}_orijinal.jpg"), orijinal)
        cv2.imwrite(str(self._debug_cikti_klasoru / f"{damga}_{ihlal.ihlal_tipi_adi}_blur.jpg"), blurlu)

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
        cv2.imshow("ISG Ihlal Tespiti - AI Core", gosterilecek)
