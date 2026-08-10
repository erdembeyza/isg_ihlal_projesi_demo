"""
OpenCV YuNet + SFace modellerini indirir (kisi tanima).

Ilk calistirmada models/ altina indirilir; egitim gerekmez — hazir ONNX modelleri.
"""
from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

# OpenCV Zoo (Apache-2.0)
YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
SFACE_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

YUNET_DOSYA = "face_detection_yunet_2023mar.onnx"
SFACE_DOSYA = "face_recognition_sface_2021dec.onnx"


def _indir(url: str, hedef: Path) -> None:
    hedef.parent.mkdir(parents=True, exist_ok=True)
    if hedef.is_file() and hedef.stat().st_size > 10_000:
        return
    logger.info("Yuz modeli indiriliyor: %s -> %s", url.split("/")[-1], hedef)
    tmp = hedef.with_suffix(hedef.suffix + ".tmp")
    try:
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(hedef)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def yuz_model_yollari(models_dir: Path) -> tuple[Path, Path]:
    """(yunet_path, sface_path) doner; yoksa indirir."""
    yunet = models_dir / YUNET_DOSYA
    sface = models_dir / SFACE_DOSYA
    _indir(YUNET_URL, yunet)
    _indir(SFACE_URL, sface)
    return yunet, sface
