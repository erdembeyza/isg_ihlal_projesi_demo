"""
MODUL-3 (tasarim_mimari.md) istemci tarafi: AI Core'un backend'e /api/auth/login
ile giris yapip aldigi JWT'yi onbellekte tutan, suresi dolmadan once kendiligiden
yenileyen kucuk bir istemci.
"""
from __future__ import annotations

import logging
import time

import requests

from .config import Ayarlar

logger = logging.getLogger(__name__)

# Backend jwt.expiration-ms varsayilani 3600000 ms (1 saat). Suresi dolmadan
# guvenli bir payla yenilemek icin bu esikten sonra token'i bayat sayariz.
TOKEN_YENILEME_ESIGI_SANIYE = 50 * 60


class BackendOturumu:
    """Backend'e karsi kimlik dogrulanmis istekler icin JWT saglayan oturum."""

    def __init__(self, ayarlar: Ayarlar):
        self._ayarlar = ayarlar
        self._token: str | None = None
        self._token_alindigi_zaman: float = 0.0

    def token_al(self, zorla_yenile: bool = False) -> str:
        token_bayat = (time.monotonic() - self._token_alindigi_zaman) > TOKEN_YENILEME_ESIGI_SANIYE
        if self._token is None or token_bayat or zorla_yenile:
            self._giris_yap()
        assert self._token is not None
        return self._token

    def _giris_yap(self) -> None:
        istek = {
            "kullaniciAdi": self._ayarlar.ai_core_kullanici_adi,
            "sifre": self._ayarlar.ai_core_sifre,
        }
        yanit = requests.post(self._ayarlar.auth_login_url, json=istek, timeout=10)
        yanit.raise_for_status()
        govde = yanit.json()
        self._token = govde["token"]
        self._token_alindigi_zaman = time.monotonic()
        logger.info(
            "AI Core backend'e giris yapti (kullanici=%s, rol=%s)",
            self._ayarlar.ai_core_kullanici_adi,
            govde.get("rol"),
        )

    def yetkili_baslik(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token_al()}"}
