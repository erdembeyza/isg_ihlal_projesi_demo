"""
MODUL-1 (tasarim_mimari.md) istemci tarafi: tespit edilen bir ihlali
IhlalKayitRequestDTO seklinde Java backend'ine (POST /api/ihlaller) gonderir.
"""
from __future__ import annotations

import base64
import logging
from datetime import datetime

import cv2
import numpy as np
import requests

from .auth_client import BackendOturumu
from .config import Ayarlar

logger = logging.getLogger(__name__)

# JPEG kalitesi: kanit fotograflarinin okunabilirligi ile base64 govde
# boyutu (agdaki gecikme) arasinda makul bir denge.
JPEG_KALITE = 85


def kareyi_base64_jpeg_yap(kare: np.ndarray) -> str:
    basarili, buffer = cv2.imencode(".jpg", kare, [cv2.IMWRITE_JPEG_QUALITY, JPEG_KALITE])
    if not basarili:
        raise RuntimeError("Kare JPEG'e kodlanamadi")
    return base64.b64encode(buffer).decode("ascii")


class IhlalBildirimHatasi(RuntimeError):
    pass


class BackendIstemcisi:
    """AI Core'un tespit ettigi ihlalleri backend'e bildirmesini saglayan istemci."""

    def __init__(self, ayarlar: Ayarlar, oturum: BackendOturumu | None = None):
        self._ayarlar = ayarlar
        self._oturum = oturum or BackendOturumu(ayarlar)

    def ihlal_bildir(
        self,
        ihlal_tipi_adi: str,
        kare: np.ndarray,
        tespit_zamani: datetime | None = None,
        bolge_id: int | None = None,
    ) -> dict:
        """Bir ihlali backend'e POST eder; olusturulan IhlalResponseDTO'yu (dict) doner.

        bolge_id: coklu kamera modunda thread bazli bolge; verilmezse .env BOLGE_ID.
        """
        istek_govdesi = {
            "bolgeId": self._ayarlar.bolge_id if bolge_id is None else bolge_id,
            "ihlalTipiId": self._ayarlar.ihlal_tipi_id(ihlal_tipi_adi),
            "tespitZamani": (tespit_zamani or datetime.now()).isoformat(timespec="seconds"),
            "orijinalFotoBase64": kareyi_base64_jpeg_yap(kare),
        }

        for deneme in (1, 2):
            try:
                yanit = requests.post(
                    self._ayarlar.ihlal_kayit_url,
                    json=istek_govdesi,
                    headers=self._oturum.yetkili_baslik(),
                    timeout=15,
                )
                if yanit.status_code == 401 and deneme == 1:
                    logger.warning("Token gecersiz/suresi dolmus, yeniden giris yapilip tekrar denenecek")
                    self._oturum.token_al(zorla_yenile=True)
                    continue
                if not yanit.ok:
                    logger.error(
                        "Ihlal bildirimi HTTP %s: %s",
                        yanit.status_code,
                        yanit.text[:500],
                    )
                yanit.raise_for_status()
                return yanit.json()
            except requests.RequestException as exc:
                if deneme == 2:
                    raise IhlalBildirimHatasi(f"Ihlal backend'e bildirilemedi: {exc}") from exc
                logger.warning("Ihlal bildirimi basarisiz oldu, tekrar denenecek: %s", exc)

        raise IhlalBildirimHatasi("Ihlal backend'e bildirilemedi (beklenmeyen akis)")
