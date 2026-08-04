"""
Mevcut PPE modelinin sinif isimlerini ve indeks sirasini yazdirir.
Roboflow'ta etiketlerken bu isimler birebir ayni olmalidir.
"""
from __future__ import annotations

from pathlib import Path

from ultralytics import YOLO

AI_CORE = Path(__file__).resolve().parents[1]
VARSAYILAN_MODEL = AI_CORE / "models" / "ppe_yolov8n.pt"


def main() -> None:
    model_yolu = VARSAYILAN_MODEL
    if not model_yolu.exists():
        raise SystemExit(f"Model bulunamadi: {model_yolu}")

    model = YOLO(str(model_yolu))
    names = model.names

    print(f"Model: {model_yolu}")
    print(f"Sinif sayisi (nc): {len(names)}\n")
    for idx, ad in sorted(names.items()):
        print(f"  {idx}: {ad}")

    print("\n--- data.yaml icin names listesi ---")
    print("names:", [names[i] for i in range(len(names))])


if __name__ == "__main__":
    main()
