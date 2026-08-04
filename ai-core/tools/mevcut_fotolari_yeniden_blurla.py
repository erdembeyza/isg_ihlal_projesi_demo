"""
Diskteki mevcut kanit fotograflarini (orijinal -> blur) KVKK blur ile yeniden uretir.

    python tools/mevcut_fotolari_yeniden_blurla.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

AI_CORE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AI_CORE))

from src.face_blur import kanit_yuzlerini_blurla  # noqa: E402


def _hog_kisi_kutulari(kare) -> list[tuple[int, int, int, int]]:
    """OpenCV HOG insan dedektoru (basarisizsa bos liste)."""
    try:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        olcek = 0.5
        kucuk = cv2.resize(kare, None, fx=olcek, fy=olcek)
        if kucuk.shape[0] < 64 or kucuk.shape[1] < 32:
            return []
        rects, _ = hog.detectMultiScale(
            kucuk, winStride=(8, 8), padding=(16, 16), scale=1.05
        )
        kutular = []
        for (x, y, w, h) in rects:
            kutular.append((
                int(x / olcek),
                int(y / olcek),
                int((x + w) / olcek),
                int((y + h) / olcek),
            ))
        return kutular
    except Exception:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Mevcut ihlal fotograflarini yeniden blurla")
    parser.add_argument(
        "--uploads",
        default=str(AI_CORE.parent / "backend" / "uploads" / "ihlaller"),
    )
    args = parser.parse_args()

    klasor = Path(args.uploads)
    if not klasor.is_dir():
        raise SystemExit(f"Klasor yok: {klasor}")

    orijinaller = sorted(klasor.glob("*_orijinal.jpg"))
    if not orijinaller:
        raise SystemExit(f"*_orijinal.jpg bulunamadi: {klasor}")

    print(f"{len(orijinaller)} orijinal foto islenecek...", flush=True)
    sayac = 0
    for orijinal_yol in orijinaller:
        blur_yol = orijinal_yol.with_name(
            orijinal_yol.name.replace("_orijinal.jpg", "_blur.jpg")
        )
        kare = cv2.imread(str(orijinal_yol))
        if kare is None:
            print(f"ATLANDI: {orijinal_yol.name}", flush=True)
            continue

        kisiler = _hog_kisi_kutulari(kare)
        blurlu = kanit_yuzlerini_blurla(kare, kisiler)
        cv2.imwrite(str(blur_yol), blurlu, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        sayac += 1
        print(f"OK {sayac}/{len(orijinaller)} {blur_yol.name} kisi={len(kisiler)}", flush=True)

    print(f"\nToplam yeniden blurlanan: {sayac}", flush=True)


if __name__ == "__main__":
    main()
