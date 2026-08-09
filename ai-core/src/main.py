"""
AI Core CLI giris noktasi — guvenlik kamerasi (RTSP) / canli izleme.

Bilgisayar webkami (guvenlik kamerasi gibi surekli):
    # .env: VIDEO_SOURCE=0
    python -m src.main --show

Gercek RTSP guvenlik kamerasi:
    # .env: VIDEO_SOURCE=rtsp://...
    python -m src.main

Coklu kamera:
    python -m src.main --cameras cameras.json

Yuksek Firin A + B (video kayitlari, ayni anda):
    python -m src.main --cameras cameras.yuksek-firin.json --show
    # veya: .\\scripts\\start-yuksek-firin.ps1

Dosya ile canli simulasyon:
    python -m src.main --source test_videos/demo2.mp4 --loop --show
"""
from __future__ import annotations

import argparse
import logging
import threading
from pathlib import Path

from .backend_client import BackendIstemcisi
from .config import ayarlari_yukle, kameralari_yukle
from .pipeline import IhlalPipeline
from .ppe_detector import PpeDedektoru
from .stream import canli_akismi


def _argumanlari_parse_et() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ISG Ihlal Tespit AI Core — canli kamera / video"
    )
    parser.add_argument(
        "--source", dest="source", default=None,
        help="Tek kaynak: RTSP URL veya dosya. Verilmezse .env VIDEO_SOURCE kullanilir.",
    )
    parser.add_argument(
        "--cameras", dest="cameras", default=None,
        help="Coklu kamera JSON dosyasi (bkz. cameras.example.json). "
             "Her kamera ayri thread'de, kendi bolge_id'si ile calisir.",
    )
    parser.add_argument(
        "--dry-run", dest="dry_run", action="store_true",
        help="Ihlalleri backend'e GONDERMEZ; yalnizca konsola loglar.",
    )
    parser.add_argument(
        "--debug-output", dest="debug_output", default=None,
        help="--dry-run ile tespit karelerini bu klasore kaydeder.",
    )
    parser.add_argument(
        "--show", dest="show", action="store_true",
        help="Tespitleri pencerede gosterir ('q' ile cikilir).",
    )
    parser.add_argument(
        "--loop", dest="loop", action="store_true",
        help="Yerel video bitince basa sar (canli kamera simulasyonu). "
             "RTSP akisinda gerekmez; zaten surekli izler.",
    )
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true",
        help="DEBUG seviyesinde loglama.",
    )
    return parser.parse_args()


def _tek_kamera_calistir(
    ayarlar,
    *,
    kaynak: str | None,
    dry_run: bool,
    goster: bool,
    debug_output: Path | None,
    loop: bool,
    dedektor: PpeDedektoru | None = None,
    backend: BackendIstemcisi | None = None,
) -> None:
    video = kaynak or ayarlar.video_kaynagi
    # Dosya ile canli hissi: --loop yoksa ama kullanici RTSP degilse uyar.
    if not canli_akismi(video) and not loop:
        logging.getLogger(__name__).info(
            "Yerel dosya modu: video bitince durur. Canli kamera gibi surekli "
            "izlemek icin --loop ekleyin veya VIDEO_SOURCE=rtsp://... kullanin."
        )

    pipeline = IhlalPipeline(
        ayarlar,
        dedektor=dedektor,
        backend=backend,
        kuru_calistirma=dry_run,
        goster=goster,
        debug_cikti_klasoru=debug_output,
    )
    pipeline.calistir(kaynak=kaynak, dongu=loop)


def _coklu_kamera_calistir(
    temel_ayarlar,
    cameras_dosyasi: str,
    *,
    dry_run: bool,
    goster: bool,
    debug_output: Path | None,
    loop: bool,
) -> None:
    kameralar = kameralari_yukle(cameras_dosyasi)
    logger = logging.getLogger(__name__)
    logger.info("%s kamera baslatilacak: %s", len(kameralar), cameras_dosyasi)

    # Backend oturumu ortak; YOLO modeli kamera basina ayri yuklenir.
    # Paylasimli tek model + kilit, B kamerasinda tespit/sure birikimini bozuyordu
    # (ekranda kutu gorunup ihlal kaydi hic dusmuyordu).
    backend = None if dry_run else BackendIstemcisi(temel_ayarlar)

    threadler: list[threading.Thread] = []
    for kamera in kameralar:
        ayar = temel_ayarlar.kamera_ile(
            video_kaynagi=kamera.video_kaynagi,
            bolge_id=kamera.bolge_id,
            kamera_adi=kamera.ad,
        )
        dedektor = PpeDedektoru(temel_ayarlar)

        def _hedef(a=ayar, d=dedektor) -> None:
            try:
                _tek_kamera_calistir(
                    a,
                    kaynak=a.video_kaynagi,
                    dry_run=dry_run,
                    goster=goster,
                    debug_output=debug_output,
                    loop=loop or (not canli_akismi(a.video_kaynagi)),
                    dedektor=d,
                    backend=backend,
                )
            except Exception:
                logging.getLogger(__name__).exception(
                    "Kamera thread'i dustu: %s", a.kamera_adi
                )

        t = threading.Thread(
            target=_hedef,
            name=f"kamera-{kamera.bolge_id}-{kamera.ad}",
            daemon=True,
        )
        threadler.append(t)
        t.start()
        logger.info(
            "Kamera thread basladi: ad=%s bolge_id=%s kaynak=%s",
            kamera.ad,
            kamera.bolge_id,
            kamera.video_kaynagi,
        )

    try:
        for t in threadler:
            t.join()
    except KeyboardInterrupt:
        logger.info("Coklu kamera durduruluyor (Ctrl+C)...")


def main() -> None:
    args = _argumanlari_parse_et()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s",
    )

    ayarlar = ayarlari_yukle()
    debug_klasor = Path(args.debug_output) if args.debug_output else None

    if args.cameras:
        _coklu_kamera_calistir(
            ayarlar,
            args.cameras,
            dry_run=args.dry_run,
            goster=args.show,
            debug_output=debug_klasor,
            loop=args.loop,
        )
    else:
        _tek_kamera_calistir(
            ayarlar,
            kaynak=args.source,
            dry_run=args.dry_run,
            goster=args.show,
            debug_output=debug_klasor,
            loop=args.loop,
        )


if __name__ == "__main__":
    main()
