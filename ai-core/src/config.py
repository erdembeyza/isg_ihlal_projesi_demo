"""
AI Core icin merkezi konfigurasyon modulu.

Tum ayarlar `.env` dosyasindan (bkz. `.env.example`) okunur; bu sayede
kaynak koduna dokunmadan farkli bolge/kamera icin ayri surecler
calistirilabilir (ör. her kameranin kendi .env'i ile).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

AI_CORE_KOK_DIZIN = Path(__file__).resolve().parent.parent


def _env_dosyasi_yukle() -> None:
    env_yolu = AI_CORE_KOK_DIZIN / ".env"
    if env_yolu.exists():
        load_dotenv(env_yolu)
    else:
        # .env yoksa (ör. yalnizca .env.example kopyalanmamis bir kurulum)
        # varsayilan degerlerle DEMO_MODU'nda calisilabilmesi icin sessizce
        # gecilir; asagidaki alanlarin hepsinin makul varsayilanlari var.
        pass


def _float_oku(anahtar: str, varsayilan: float) -> float:
    return float(os.getenv(anahtar, varsayilan))


def _int_oku(anahtar: str, varsayilan: int) -> int:
    return int(os.getenv(anahtar, varsayilan))


def _yol_coz(deger: str) -> Path:
    """Goreli yollari ai-core kok dizinine gore, mutlak yollari oldugu gibi cozer."""
    yol = Path(deger)
    return yol if yol.is_absolute() else (AI_CORE_KOK_DIZIN / yol)


@dataclass(frozen=True)
class Ayarlar:
    backend_base_url: str
    ai_core_kullanici_adi: str
    ai_core_sifre: str
    video_kaynagi: str
    yolo_model_yolu: Path
    guven_esigi: float
    bolge_id: int
    ihlal_tipi_id_baret: int
    ihlal_tipi_id_yelek: int
    ihlal_tipi_id_gozluk: int
    detection_cooldown_saniye: float
    frame_atlama: int

    @property
    def auth_login_url(self) -> str:
        return f"{self.backend_base_url.rstrip('/')}/api/auth/login"

    @property
    def ihlal_kayit_url(self) -> str:
        return f"{self.backend_base_url.rstrip('/')}/api/ihlaller"

    def ihlal_tipi_id(self, ihlal_tipi_adi: str) -> int:
        eslestirme = {
            "BARET": self.ihlal_tipi_id_baret,
            "YELEK": self.ihlal_tipi_id_yelek,
            "GOZLUK": self.ihlal_tipi_id_gozluk,
        }
        try:
            return eslestirme[ihlal_tipi_adi]
        except KeyError as exc:
            raise ValueError(f"Bilinmeyen ihlal tipi: {ihlal_tipi_adi}") from exc


def ayarlari_yukle() -> Ayarlar:
    _env_dosyasi_yukle()

    video_kaynagi = os.getenv("VIDEO_SOURCE", "test_videos/ornek_video.mp4")
    # RTSP/HTTP akislari oldugu gibi birakilir; yalnizca yerel dosya yollari
    # ai-core kok dizinine gore cozulur.
    if not video_kaynagi.lower().startswith(("rtsp://", "http://", "https://")):
        video_kaynagi = str(_yol_coz(video_kaynagi))

    return Ayarlar(
        backend_base_url=os.getenv("BACKEND_BASE_URL", "http://localhost:8080"),
        ai_core_kullanici_adi=os.getenv("AI_CORE_KULLANICI_ADI", "ai_core_servis"),
        ai_core_sifre=os.getenv("AI_CORE_SIFRE", "AiCore123!"),
        video_kaynagi=video_kaynagi,
        yolo_model_yolu=_yol_coz(os.getenv("YOLO_MODEL_PATH", "models/ppe_yolov8n.pt")),
        guven_esigi=_float_oku("CONFIDENCE_THRESHOLD", 0.5),
        bolge_id=_int_oku("BOLGE_ID", 1),
        ihlal_tipi_id_baret=_int_oku("IHLAL_TIPI_ID_BARET", 1),
        ihlal_tipi_id_yelek=_int_oku("IHLAL_TIPI_ID_YELEK", 2),
        ihlal_tipi_id_gozluk=_int_oku("IHLAL_TIPI_ID_GOZLUK", 3),
        detection_cooldown_saniye=_float_oku("DETECTION_COOLDOWN_SANIYE", 30.0),
        frame_atlama=max(1, _int_oku("FRAME_ATLAMA", 2)),
    )
