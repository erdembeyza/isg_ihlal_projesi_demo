"""
Gelistirme/kalibrasyon amacli kucuk bir test videosu uretir.

Kaggle'daki gercek ISG ihlali videolarina internet erisimi olmayan bir
gelistirme ortaminda (bkz. ai-core/README.md), ultralytics paketiyle birlikte
gelen ornek gorsellerden (icinde gercek insanlar bulunan 'bus.jpg') kisa bir
test videosu uretilerek DEMO_MODU'ndaki uctan uca boru hatti (kisi tespiti ->
blur -> backend POST) dogrulanabilir.

Kullanim:
    python tools/test_video_uret.py [--cikti test_videos/demo.mp4] [--kare-sayisi 30]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2

KOK_DIZIN = Path(__file__).resolve().parent.parent


def _ornek_gorseli_bul() -> Path:
    """ultralytics paketiyle birlikte gelen ornek gorseli (icinde insan olan) bulur."""
    from ultralytics.utils import ASSETS

    aday = Path(ASSETS) / "bus.jpg"
    if aday.exists():
        return aday
    raise FileNotFoundError(
        "ultralytics ornek gorseli bulunamadi; 'pip install ultralytics' sonrasi "
        "paketle birlikte gelen assets klasoru bekleniyordu."
    )


def uret(cikti_yolu: Path, kare_sayisi: int, fps: int = 10) -> None:
    gorsel_yolu = _ornek_gorseli_bul()
    gorsel = cv2.imread(str(gorsel_yolu))
    if gorsel is None:
        raise RuntimeError(f"Ornek gorsel okunamadi: {gorsel_yolu}")

    yukseklik, genislik = gorsel.shape[:2]
    cikti_yolu.parent.mkdir(parents=True, exist_ok=True)

    yazici = cv2.VideoWriter(
        str(cikti_yolu), cv2.VideoWriter_fourcc(*"mp4v"), fps, (genislik, yukseklik)
    )
    try:
        for _ in range(kare_sayisi):
            yazici.write(gorsel)
    finally:
        yazici.release()

    print(f"Test videosu uretildi: {cikti_yolu} ({kare_sayisi} kare, {fps} fps, kaynak: {gorsel_yolu.name})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Core icin kucuk bir demo/test videosu uretir")
    parser.add_argument("--cikti", default=str(KOK_DIZIN / "test_videos" / "demo.mp4"))
    parser.add_argument("--kare-sayisi", type=int, default=30)
    parser.add_argument("--fps", type=int, default=10)
    args = parser.parse_args()

    uret(Path(args.cikti), args.kare_sayisi, args.fps)
