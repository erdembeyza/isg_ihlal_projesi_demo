"""
Mevcut PPE modelini (ppe_yolov8n.pt) az sayida yeni gorselle fine-tune eder.

Kullanim (ai-core venv aktif):
    cd ai-core
    python training/egitim_scripti.py

Cikti:
    runs/detect/isg_guncellenmis_model/weights/best.pt
"""
from __future__ import annotations

import sys
from pathlib import Path

from ultralytics import YOLO

AI_CORE = Path(__file__).resolve().parents[1]
MEVCUT_MODEL = AI_CORE / "models" / "ppe_yolov8n.pt"
DATA_YAML = AI_CORE / "training" / "yeni_veri_seti" / "data.yaml"
CIKTI_ADI = "isg_guncellenmis_model"


def _siniflari_dogrula(model: YOLO, data_yaml: Path) -> None:
    """data.yaml names listesi mevcut modelle uyusmuyorsa uyar."""
    import yaml

    with data_yaml.open(encoding="utf-8") as f:
        veri = yaml.safe_load(f)

    yaml_names = list(veri.get("names", []))
    model_names = [model.names[i] for i in range(len(model.names))]

    if yaml_names != model_names:
        print("HATA: data.yaml sinif listesi mevcut modelle uyusmuyor!", file=sys.stderr)
        print(f"  Model ({len(model_names)}): {model_names}", file=sys.stderr)
        print(f"  YAML  ({len(yaml_names)}): {yaml_names}", file=sys.stderr)
        print(
            "  Roboflow'ta etiket isimlerini ve data.yaml names sirasini duzeltin.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def main() -> None:
    if not MEVCUT_MODEL.exists():
        raise SystemExit(
            f"Mevcut model bulunamadi: {MEVCUT_MODEL}\n"
            "Once models/ppe_yolov8n.pt dosyasini yerlestirin."
        )

    if not DATA_YAML.exists():
        raise SystemExit(
            f"Veri dosyasi bulunamadi: {DATA_YAML}\n"
            "Roboflow'tan YOLOv8 verisini indirip training/yeni_veri_seti/ "
            "klasorune cikartin ve data.yaml olusturun.\n"
            "Ornek: training/data.yaml.example"
        )

    model = YOLO(str(MEVCUT_MODEL))
    _siniflari_dogrula(model, DATA_YAML)

    print(f"Model: {MEVCUT_MODEL}")
    print(f"Veri : {DATA_YAML}")
    print("Fine-tune basliyor (dusuk ogrenme orani, freeze=10)...\n")

    model.train(
        data=str(DATA_YAML),
        epochs=30,
        imgsz=640,
        batch=8,
        lr0=0.0001,
        lrf=0.01,
        freeze=10,
        project=str(AI_CORE / "runs" / "detect"),
        name=CIKTI_ADI,
        exist_ok=True,
    )

    best = AI_CORE / "runs" / "detect" / CIKTI_ADI / "weights" / "best.pt"
    print("\n--- Egitim tamamlandi ---")
    print(f"Yeni model: {best}")
    print("\nUretime almak icin:")
    print(f"  copy \"{best}\" \"{MEVCUT_MODEL}\"")


if __name__ == "__main__":
    main()
