"""
KVKK: kanit fotosunda yalnizca INSAN yuzlerini karelerle bulaniklastirir.

- Blur sadece YOLO kisi kutusu icindeki yuzlere uygulanir (nesne/arka plan degil).
- Birden fazla kisi varsa her birinin yuzu ayri kare olarak blurlanir.
- Haar kutusu genelde dar kaldigi icin bas/yuz karesi genisletilir (sac, alin, cene).
"""
from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

_CASCADES: list[cv2.CascadeClassifier] = []
_CASCADE_YUKLENDI = False

# Haar yuz kutusu dar gelir; asimetrik pad ile tam bas kapsansin.
_PAD_UST = 0.55
_PAD_ALT = 0.45
_PAD_YAN = 0.50
# Yuz bulunamazsa bas icin kare (kisi yuksekliginin orani).
_YEDEK_BAS_ORAN = 0.38


def _cascade_yukle() -> list[cv2.CascadeClassifier]:
    global _CASCADES, _CASCADE_YUKLENDI
    if _CASCADE_YUKLENDI:
        return _CASCADES
    _CASCADE_YUKLENDI = True

    adaylar = [
        Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml",
        Path(cv2.data.haarcascades) / "haarcascade_frontalface_alt2.xml",
        Path(cv2.data.haarcascades) / "haarcascade_profileface.xml",
    ]
    for yol in adaylar:
        if not yol.is_file():
            continue
        siniflandirici = cv2.CascadeClassifier(str(yol))
        if not siniflandirici.empty():
            _CASCADES.append(siniflandirici)
            logger.info("Yuz cascade yuklendi: %s", yol.name)

    if not _CASCADES:
        logger.warning("OpenCV Haar yuz cascade bulunamadi; yuz blur kisitli calisacak.")
    return _CASCADES


def _kare_blurla(kare: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> None:
    """Yuz/bas karesini guclu blurla (yerinde)."""
    h, w = kare.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 - x1 < 4 or y2 - y1 < 4:
        return
    roi = kare[y1:y2, x1:x2]
    kenar = max(x2 - x1, y2 - y1)
    k = max(31, (kenar // 2) | 1)
    k = min(k, 99)
    # Iki gecis: kimlik ozellikleri daha guclu silinsin.
    bulanik = cv2.GaussianBlur(roi, (k, k), 0)
    kare[y1:y2, x1:x2] = cv2.GaussianBlur(bulanik, (k, k), 0)


def _asimetrik_pad(
    x1: int, y1: int, x2: int, y2: int
) -> tuple[int, int, int, int]:
    bw, bh = max(1, x2 - x1), max(1, y2 - y1)
    return (
        x1 - int(bw * _PAD_YAN),
        y1 - int(bh * _PAD_UST),
        x2 + int(bw * _PAD_YAN),
        y2 + int(bh * _PAD_ALT),
    )


def _bas_karesine_genislet(
    yuz: tuple[int, int, int, int],
    kisi: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    """
    Haar kutusu goz-burun-agiz civarinda kalir; tam bas icin kareyi buyut.
    Kenar, kisi genisligi/yuksekligine gore alt sinirla genis tutulur.
    """
    fx1, fy1, fx2, fy2 = _asimetrik_pad(*yuz)
    kx1, ky1, kx2, ky2 = kisi
    kw, kh = max(1, kx2 - kx1), max(1, ky2 - ky1)

    fw, fh = max(1, fx2 - fx1), max(1, fy2 - fy1)
    kenar = max(fw, fh, int(kw * 0.42), int(kh * 0.22))
    kenar = min(kenar, int(kw * 0.95), int(kh * 0.55))

    cx = (fx1 + fx2) // 2
    # Alin/sac icin merkezi biraz yukari kaydir.
    cy = (fy1 + fy2) // 2 - int(kenar * 0.08)
    bx1, by1 = cx - kenar // 2, cy - kenar // 2
    bx2, by2 = bx1 + kenar, by1 + kenar

    # Kisi kutusu disina tasmasin (arka plan blur olmasin); ustte hafif tolerans.
    tol_ust = int(kh * 0.06)
    bx1 = max(kx1, bx1)
    by1 = max(ky1 - tol_ust, by1)
    bx2 = min(kx2, bx2)
    by2 = min(ky2, by2)
    return bx1, by1, bx2, by2


def _kutulari_birlestir(
    kutular: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    """Cakisan yuz kutularini tek karede birlestir."""
    if len(kutular) <= 1:
        return kutular

    def iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
        if inter <= 0:
            return 0.0
        area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
        area_b = max(1, (bx2 - bx1) * (by2 - by1))
        return inter / float(area_a + area_b - inter)

    kalan = sorted(kutular, key=lambda k: (k[2] - k[0]) * (k[3] - k[1]), reverse=True)
    sonuc: list[tuple[int, int, int, int]] = []
    while kalan:
        a = kalan.pop(0)
        birlesen = [a]
        sonraki: list[tuple[int, int, int, int]] = []
        for b in kalan:
            if iou(a, b) >= 0.25:
                birlesen.append(b)
            else:
                sonraki.append(b)
        x1 = min(k[0] for k in birlesen)
        y1 = min(k[1] for k in birlesen)
        x2 = max(k[2] for k in birlesen)
        y2 = max(k[3] for k in birlesen)
        sonuc.append((x1, y1, x2, y2))
        kalan = sonraki
    return sonuc


def _kisi_ici_yuzleri_bul(
    gri: np.ndarray, kisi: tuple[int, int, int, int]
) -> list[tuple[int, int, int, int]]:
    """Sadece kisi ROI icinde yuz ara (tam kare false-positive azaltir)."""
    cascades = _cascade_yukle()
    if not cascades:
        return []

    kx1, ky1, kx2, ky2 = kisi
    h, w = gri.shape[:2]
    kx1, ky1 = max(0, kx1), max(0, ky1)
    kx2, ky2 = min(w, kx2), min(h, ky2)
    if kx2 - kx1 < 20 or ky2 - ky1 < 20:
        return []

    # Yuz genelde ust bolgede; kask/bas icin ust %70.
    ust_y2 = ky1 + int((ky2 - ky1) * 0.70)
    roi = gri[ky1:ust_y2, kx1:kx2]
    if roi.size == 0:
        return []

    min_kenar = max(14, int(min(kx2 - kx1, ky2 - ky1) * 0.06))
    ham_kutular: list[tuple[int, int, int, int]] = []
    roi_w = roi.shape[1]
    # Normal + ayna (saga bakan profil yuzler).
    for kaynak, ayna in ((roi, False), (cv2.flip(roi, 1), True)):
        for cascade in cascades:
            ham = cascade.detectMultiScale(
                kaynak,
                scaleFactor=1.05,
                minNeighbors=4,
                minSize=(min_kenar, min_kenar),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
            for (x, y, ww, hh) in ham:
                oran = ww / max(1, hh)
                if oran < 0.55 or oran > 1.60:
                    continue
                if ayna:
                    x = roi_w - x - ww
                ham_kutular.append(
                    (kx1 + int(x), ky1 + int(y), kx1 + int(x + ww), ky1 + int(y + hh))
                )

    return _kutulari_birlestir(ham_kutular)


def _yedek_bas_karesi(kisi: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Yuz bulunamazsa kisi ust-orta bas karesi (yuzu tam kaplayacak kadar buyuk)."""
    x1, y1, x2, y2 = kisi
    kw, kh = max(1, x2 - x1), max(1, y2 - y1)
    kenar = max(36, int(kh * _YEDEK_BAS_ORAN))
    kenar = min(kenar, int(kw * 0.90), int(kh * 0.50))
    cx = (x1 + x2) // 2
    # Ustten biraz asagi — kask/bas merkezi.
    cy = y1 + int(kh * 0.12) + kenar // 2
    return cx - kenar // 2, cy - kenar // 2, cx + kenar // 2, cy + kenar // 2


def yuzleri_blurla(
    kare: np.ndarray,
    kisi_kutulari: list[tuple[int, int, int, int]] | None = None,
) -> np.ndarray:
    """
    Yalnizca insan (kisi_kutulari) icindeki yuzleri karelerle blurlar.
    kisi_kutulari yoksa veya bossa hicbir sey blurlanmaz.
    """
    if kare is None or kare.size == 0:
        return kare
    if not kisi_kutulari:
        logger.debug("Kisi kutusu yok; yuz blur atlandi")
        return kare.copy()

    sonuc = kare.copy()
    gri = cv2.cvtColor(sonuc, cv2.COLOR_BGR2GRAY)
    gri = cv2.equalizeHist(gri)

    blur_sayisi = 0
    for kisi in kisi_kutulari:
        yuzler = _kisi_ici_yuzleri_bul(gri, kisi)
        if yuzler:
            for yuz in yuzler:
                _kare_blurla(sonuc, *_bas_karesine_genislet(yuz, kisi))
                blur_sayisi += 1
        else:
            _kare_blurla(sonuc, *_yedek_bas_karesi(kisi))
            blur_sayisi += 1

    logger.debug("%s insan icin %s yuz/bas karesi blurlanadi", len(kisi_kutulari), blur_sayisi)
    return sonuc
