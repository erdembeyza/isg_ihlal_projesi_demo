"""
AI Core CLI giris noktasi.

Kullanim ornekleri:
    # .env'deki VIDEO_SOURCE ile canli/rtsp modda calistir, ihlalleri backend'e gonder
    python -m src.main

    # Yerel bir test videosuyla, backend'e HICBIR SEY GONDERMEDEN kalibrasyon yap
    python -m src.main --source test_videos/demo.mp4 --dry-run --show

    # Test videosunu sonsuz dongude oynat (canli akisi simule etmek icin)
    python -m src.main --source test_videos/demo.mp4 --loop
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import ayarlari_yukle
from .pipeline import IhlalPipeline
from .ppe_detector import PpeDedektoru


def _argumanlari_parse_et() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ISG Ihlal Tespit AI Core")
    parser.add_argument(
        "--source", dest="source", default=None,
        help="Video kaynagi (RTSP URL ya da dosya yolu). Verilmezse .env'deki VIDEO_SOURCE kullanilir.",
    )
    parser.add_argument(
        "--dry-run", dest="dry_run", action="store_true",
        help="Ihlalleri backend'e GONDERMEZ; yalnizca konsola loglar (kalibrasyon modu).",
    )
    parser.add_argument(
        "--debug-output", dest="debug_output", default=None,
        help="--dry-run ile birlikte kullanildiginda, tespit edilen (orijinal, blurlu) kareleri bu klasore kaydeder.",
    )
    parser.add_argument(
        "--show", dest="show", action="store_true",
        help="Tespitleri kutu/etiketle birlikte bir pencerede gosterir ('q' ile cikilir).",
    )
    parser.add_argument(
        "--loop", dest="loop", action="store_true",
        help="Video dosyasi bittiginde basa sararak sonsuz dongude oynatir (canli akis simulasyonu).",
    )
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true",
        help="DEBUG seviyesinde loglama acar.",
    )
    return parser.parse_args()


def main() -> None:
    args = _argumanlari_parse_et()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    ayarlar = ayarlari_yukle()
    dedektor = PpeDedektoru(ayarlar)

    pipeline = IhlalPipeline(
        ayarlar,
        dedektor=dedektor,
        kuru_calistirma=args.dry_run,
        goster=args.show,
        debug_cikti_klasoru=Path(args.debug_output) if args.debug_output else None,
    )
    pipeline.calistir(kaynak=args.source, dongu=args.loop)


if __name__ == "__main__":
    main()
