"""
Diskteki mevcut kanit fotograflarini (orijinal -> blur) KVKK blur ile yeniden uretir.

Kullanim (ai-core klasorunden, backend kapali olsa da olur):
    python tools/mevcut_fotolari_yeniden_blurla.py
    python tools/mevcut_fotolari_yeniden_blurla.py --uploads ../backend/uploads/ihlaller
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

# ai-core/src import yolu
AI_CORE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AI_CORE))

from src.face_blur import kanit_yuzlerini_blurla  # noqa: E402
from src.ppe_detector import KISI_SINIF_ISIMLERI  # noqa: E402


def _kisi_kutularini_bul(kare, model) -> list[tuple[int, int, int, int]]:
    if model is None:
        return []
    sonuclar = model.predict(kare, conf=0.35, verbose=False)
    if not sonuclar or sonuclar[0].boxes is None:
        return []
    kutular = []
    isimler = sonuclar[0].names
    for kutu in sonuclar[0].boxes:
        sinif_adi = isimler.get(int(kutu.cls[0]), "")
        x1, y1, x2, y2 = (int(v) for v in kutu.xyxy[0])
        # Person veya PPE-eksik siniflari (kisi uzerinde) bas blur icin kullan
        if sinif_adi in KISI_SINIF_ISIMLERI or sinif_adi.startswith("NO-"):
            kutular.append((x1, y1, x2, y2))
    return kutular


def main() -> None:
    parser = argparse.ArgumentParser(description="Mevcut ihlal fotograflarini yeniden blurla")
    parser.add_argument(
        "--uploads",
        default=str(AI_CORE.parent / "backend" / "uploads" / "ihlaller"),
        help="orijinal/blur jpg klasoru",
    )
    parser.add_argument(
        "--model",
        default=str(AI_CORE / "models" / "ppe_yolov8n.pt"),
        help="Kisi kutusu icin YOLO modeli (yoksa sadece Haar)",
    )
    args = parser.parse_args()

    klasor = Path(args.uploads)
    if not klasor.is_dir():
        raise SystemExit(f"Klasor yok: {klasor}")

    model = None
    model_yolu = Path(args.model)
    if model_yolu.is_file():
        from ultralytics import YOLO

        print(f"YOLO yukleniyor: {model_yolu}")
        model = YOLO(str(model_yolu))
    else:
        print("UYARI: YOLO yok; yalnizca Haar + varsayilan bas blur kullanilacak.")

    orijinaller = sorted(klasor.glob("*_orijinal.jpg"))
    if not orijinaller:
        raise SystemExit(f"*_orijinal.jpg bulunamadi: {klasor}")

    sayac = 0
    for orijinal_yol in orijinaller:
        blur_yol = Path(str(orijinal_yol).replace("_orijinal.jpg", "_blur.jpg"))
        # UUID_orijinal.jpg -> ayni uuid ile biten blur yoksa yakin isimli ara
        if not blur_yol.is_file():
            # Farkli uuid'li blur dosyalari olabilir; orijinal uzerinden yeni blur yaz
            blur_yol = orijinal_yol.with_name(
                orijinal_yol.name.replace("_orijinal.jpg", "_blur.jpg")
            )

        kare = cv2.imread(str(orijinal_yol))
        if kare is None:
            print(f"ATLANDI (okunamadi): {orijinal_yol.name}")
            continue

        kisiler = _kisi_kutularini_bul(kare, model)
        blurlu = kanit_yuzlerini_blurla(kare, kisiler)
        cv2.imwrite(str(blur_yol), blurlu, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        sayac += 1
        print(f"OK {orijinal_yol.name} -> {blur_yol.name} (kisi={len(kisiler)})")

    print(f"\nToplam yeniden blurlanan: {sayac}")


if __name__ == "__main__":
    main()
