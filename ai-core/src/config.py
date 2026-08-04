"""
AI Core icin merkezi konfigurasyon modulu.

Tum ayarlar `.env` dosyasindan (bkz. `.env.example`) okunur; bu sayede
kaynak koduna dokunmadan farkli bolge/kamera icin ayri surecler
calistirilabilir. Coklu kamera icin `cameras.json` kullanilir
(bkz. cameras.example.json).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path

from dotenv import load_dotenv

AI_CORE_KOK_DIZIN = Path(__file__).resolve().parent.parent


def _env_dosyasi_yukle() -> None:
    env_yolu = AI_CORE_KOK_DIZIN / ".env"
    if env_yolu.exists():
        load_dotenv(env_yolu)


def _float_oku(anahtar: str, varsayilan: float) -> float:
    return float(os.getenv(anahtar, str(varsayilan)))


def _int_oku(anahtar: str, varsayilan: int) -> int:
    return int(os.getenv(anahtar, str(varsayilan)))


def _bool_oku(anahtar: str, varsayilan: bool) -> bool:
    ham = os.getenv(anahtar)
    if ham is None:
        return varsayilan
    return ham.strip().lower() in {"1", "true", "yes", "on", "evet"}


def _yol_coz(deger: str) -> Path:
    """Goreli yollari ai-core kok dizinine gore, mutlak yollari oldugu gibi cozer."""
    yol = Path(deger)
    return yol if yol.is_absolute() else (AI_CORE_KOK_DIZIN / yol)


def video_kaynagini_coz(video_kaynagi: str) -> str:
    """
    Webcam (0 / webcam), RTSP/HTTP oldugu gibi birakilir;
    yerel dosya yollari ai-core kokune gore cozulur.
    """
    from .stream import _WEBCAM_ALIASLARI

    k = (video_kaynagi or "").strip()
    if k.lower() in _WEBCAM_ALIASLARI:
        return "0"
    if k.isdigit():
        return k
    if k.lower().startswith(("rtsp://", "rtsps://", "http://", "https://")):
        return k
    return str(_yol_coz(k))


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
    stream_yeniden_baglan_saniye: float
    stream_max_yeniden_baglanma: int
    stream_buffer_size: int
    stream_rtsp_tcp: bool
    kamera_adi: str = ""

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

    def kamera_ile(self, *, video_kaynagi: str, bolge_id: int, kamera_adi: str = "") -> Ayarlar:
        return replace(
            self,
            video_kaynagi=video_kaynagini_coz(video_kaynagi),
            bolge_id=bolge_id,
            kamera_adi=kamera_adi,
        )


@dataclass(frozen=True)
class KameraTanimi:
    ad: str
    bolge_id: int
    video_kaynagi: str


def ayarlari_yukle() -> Ayarlar:
    _env_dosyasi_yukle()

    video_kaynagi = video_kaynagini_coz(
        os.getenv("VIDEO_SOURCE", "test_videos/demo1.mp4")
    )

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
        stream_yeniden_baglan_saniye=max(1.0, _float_oku("STREAM_YENIDEN_BAGLAN_SANIYE", 5.0)),
        stream_max_yeniden_baglanma=_int_oku("STREAM_MAX_YENIDEN_BAGLANMA", -1),
        stream_buffer_size=max(1, _int_oku("STREAM_BUFFER_SIZE", 1)),
        stream_rtsp_tcp=_bool_oku("STREAM_RTSP_TCP", True),
        kamera_adi=os.getenv("KAMERA_ADI", "").strip(),
    )


def kameralari_yukle(dosya_yolu: str | Path) -> list[KameraTanimi]:
    """cameras.json formatini okur (bkz. cameras.example.json)."""
    yol = Path(dosya_yolu)
    if not yol.is_absolute():
        yol = AI_CORE_KOK_DIZIN / yol
    if not yol.is_file():
        raise FileNotFoundError(f"Kamera konfigurasyonu bulunamadi: {yol}")

    with yol.open(encoding="utf-8") as f:
        veri = json.load(f)

    if not isinstance(veri, list) or not veri:
        raise ValueError("cameras.json bir kamera listesi olmali (bos olamaz)")

    kameralar: list[KameraTanimi] = []
    for i, kayit in enumerate(veri):
        if not isinstance(kayit, dict):
            raise ValueError(f"cameras.json[{i}] nesne olmali")
        try:
            ad = str(kayit.get("name") or kayit.get("ad") or f"kamera-{i + 1}")
            bolge_id = int(kayit["bolge_id"])
            video_kaynagi = str(kayit.get("video_source") or kayit["video_kaynagi"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"cameras.json[{i}] icin name/bolge_id/video_source zorunlu"
            ) from exc
        kameralar.append(
            KameraTanimi(ad=ad, bolge_id=bolge_id, video_kaynagi=video_kaynagi)
        )
    return kameralar
