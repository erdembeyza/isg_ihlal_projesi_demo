"""
Canli kamera / video kaynagi yardimcilari.

Desteklenen kaynaklar:
- Bilgisayar webkami: "0", "webcam", "bilgisayar" (OpenCV cihaz indeksi)
- Guvenlik kamerasi RTSP: rtsp://...
- Yerel test videosu: dosya yolu
"""
from __future__ import annotations

import logging
import os
import sys
import time
from typing import Callable

import cv2

logger = logging.getLogger(__name__)

_WEBCAM_ALIASLARI = frozenset({
    "webcam", "camera", "cam", "bilgisayar", "pc", "laptop", "built-in",
})


def kaynak_normalize(kaynak: str | int) -> str | int:
    """'webcam' / '0' -> int cihaz indeksi; RTSP/dosya string kalir."""
    if isinstance(kaynak, int):
        return kaynak
    k = (kaynak or "").strip()
    if not k:
        raise ValueError("Video kaynagi bos olamaz")
    if k.lower() in _WEBCAM_ALIASLARI:
        return 0
    if k.isdigit():
        return int(k)
    return k


def canli_akismi(kaynak: str | int) -> bool:
    """Webcam, RTSP ve HTTP akislari canli; yerel dosya degil."""
    n = kaynak_normalize(kaynak)
    if isinstance(n, int):
        return True
    k = n.lower()
    return k.startswith(("rtsp://", "rtsps://", "http://", "https://"))


def webcam_mi(kaynak: str | int) -> bool:
    return isinstance(kaynak_normalize(kaynak), int)


def yakalayici_ac(
    kaynak: str | int,
    *,
    buffer_size: int = 1,
    rtsp_tcp: bool = True,
) -> cv2.VideoCapture:
    """
    VideoCapture acar.
    - Webcam (Windows): DirectShow (CAP_DSHOW) — daha stabil
    - RTSP: FFMPEG + istege bagli TCP
    """
    n = kaynak_normalize(kaynak)

    if isinstance(n, int):
        if sys.platform.startswith("win"):
            yakalayici = cv2.VideoCapture(n, cv2.CAP_DSHOW)
            if not yakalayici.isOpened():
                yakalayici.release()
                yakalayici = cv2.VideoCapture(n)
        else:
            yakalayici = cv2.VideoCapture(n)
        if yakalayici.isOpened() and buffer_size > 0:
            try:
                yakalayici.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            except Exception:
                pass
        return yakalayici

    if canli_akismi(n) and rtsp_tcp:
        mevcut = os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS", "")
        if "rtsp_transport" not in mevcut.lower():
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

    yakalayici = cv2.VideoCapture(n, cv2.CAP_FFMPEG)
    if not yakalayici.isOpened():
        yakalayici.release()
        yakalayici = cv2.VideoCapture(n)

    if yakalayici.isOpened() and buffer_size > 0:
        try:
            yakalayici.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
        except Exception:
            logger.debug("CAP_PROP_BUFFERSIZE ayarlanamadi (kaynak=%s)", n)

    return yakalayici


def akisi_surdur(
    kaynak: str | int,
    *,
    canli: bool,
    dongu_dosya: bool,
    buffer_size: int,
    rtsp_tcp: bool,
    yeniden_baglan_saniye: float,
    max_yeniden_baglanma: int,
    kare_isle: Callable[[object], bool],
) -> None:
    """Kaynaktan kare okuyup kare_isle'ye verir. Canlida kopunca yeniden baglanir."""
    deneme = 0
    yakalayici: cv2.VideoCapture | None = None
    kaynak_etiket = kaynak_normalize(kaynak)

    def _kapat() -> None:
        nonlocal yakalayici
        if yakalayici is not None:
            try:
                yakalayici.release()
            except Exception:
                pass
            yakalayici = None

    def _dosyayi_basa_sar() -> None:
        """
        Yerel videoda POS_FRAMES=0 bazi MP4'lerde (ozellikle A kaydi) calismaz;
        EOF sonrasi isOpened False olabilir. Guvenli yol: kapatip yeniden ac.
        """
        nonlocal deneme
        logger.info("Video bitti, basa sariliyor (yeniden aciliyor): %s", kaynak_etiket)
        _kapat()
        deneme = 0

    try:
        while True:
            if yakalayici is None or not yakalayici.isOpened():
                _kapat()
                logger.info("Video kaynagi aciliyor: %s", kaynak_etiket)
                yakalayici = yakalayici_ac(
                    kaynak_etiket, buffer_size=buffer_size, rtsp_tcp=rtsp_tcp
                )
                if not yakalayici.isOpened():
                    deneme += 1
                    # Dongulu dosya: gecici acilamama yuzunden pipeline olmesin.
                    if not canli and not dongu_dosya and deneme >= 1:
                        raise RuntimeError(
                            f"Video kaynagi acilamadi: {kaynak_etiket}. "
                            "Webcam icin Windows kamera iznini kontrol edin."
                        )
                    if max_yeniden_baglanma >= 0 and deneme > max_yeniden_baglanma:
                        raise RuntimeError(
                            f"Video kaynagi acilamadi (max deneme): {kaynak_etiket}"
                        )
                    logger.warning(
                        "Kaynak acilamadi, %.1fs sonra tekrar (deneme=%s): %s",
                        yeniden_baglan_saniye,
                        deneme,
                        kaynak_etiket,
                    )
                    time.sleep(yeniden_baglan_saniye)
                    continue
                deneme = 0
                if webcam_mi(kaynak_etiket):
                    logger.info(
                        "Bilgisayar kamerasi acildi (cihaz=%s). "
                        "Guvenlik kamerasi gibi surekli izleniyor.",
                        kaynak_etiket,
                    )

            basarili, kare = yakalayici.read()
            if not basarili or kare is None:
                if canli:
                    deneme += 1
                    logger.warning(
                        "Canli akis koptu, %.1fs sonra yeniden baglanilacak (deneme=%s)",
                        yeniden_baglan_saniye,
                        deneme,
                    )
                    _kapat()
                    if max_yeniden_baglanma >= 0 and deneme > max_yeniden_baglanma:
                        raise RuntimeError(
                            f"Canli akis yeniden baglanamadi: {kaynak_etiket}"
                        )
                    time.sleep(yeniden_baglan_saniye)
                    continue

                if dongu_dosya:
                    _dosyayi_basa_sar()
                    continue

                logger.info("Video kaynagi bitti, pipeline durduruluyor.")
                break

            try:
                devam = kare_isle(kare)
            except Exception:
                logger.exception(
                    "Kare isleme hatasi (kaynak=%s); akis devam ediyor.",
                    kaynak_etiket,
                )
                continue

            if not devam:
                break
    finally:
        _kapat()
