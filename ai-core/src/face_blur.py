"""
MODUL-1 (tasarim_mimari.md): KVKK geregi ihlal kanit fotograflarinin blurlu
(yuzu sansurlenmis) kopyasini ureten yardimci modul.

Yuz tespiti icin ek bir model indirmeye gerek kalmamasi adina opencv-python
paketiyle birlikte gelen Haar Cascade siniflandiricisi kullanilir. Yuz hicbir
acidan tespit edilemezse (ör. profil/arka donuk pozlar), KVKK riskini sifira
indirmek icin kisi kutusunun ust ceyregi (bas bolgesinin oldugu alan)
guvenlik agi olarak yine de blurlanir.
"""
from __future__ import annotations

import cv2
import numpy as np

_yuz_dedektoru: cv2.CascadeClassifier | None = None


def _dedektoru_al() -> cv2.CascadeClassifier:
    global _yuz_dedektoru
    if _yuz_dedektoru is None:
        cascade_yolu = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _yuz_dedektoru = cv2.CascadeClassifier(cascade_yolu)
    return _yuz_dedektoru


def _blur_uygula(kare: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    x, y = max(0, x), max(0, y)
    x2, y2 = min(kare.shape[1], x + w), min(kare.shape[0], y + h)
    if x2 <= x or y2 <= y:
        return
    bolge = kare[y:y2, x:x2]
    # Kernel boyutu bolge boyutuna gore olceklenir ve tek sayi olmasi garantilenir
    # (GaussianBlur ciftlerde hata verir); cok kucuk bolgelerde en az 3 kullanilir.
    k = max(3, (min(bolge.shape[:2]) // 2) | 1)
    kare[y:y2, x:x2] = cv2.GaussianBlur(bolge, (k, k), 0)


def kisi_yuzunu_blurla(kare: np.ndarray, kisi_kutusu: tuple[int, int, int, int]) -> np.ndarray:
    """
    Verilen karenin kopyasinda, kisi_kutusu (x1, y1, x2, y2) ile sinirlanan
    alan icindeki yuzu (bulunabilirse) veya guvenlik agi olarak kutunun ust
    ceyregini Gaussian blur ile sansurler. Orijinal kare degistirilmez.
    """
    blurlu = kare.copy()
    x1, y1, x2, y2 = kisi_kutusu
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(kare.shape[1], x2), min(kare.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return blurlu

    kisi_bolgesi = blurlu[y1:y2, x1:x2]
    gri = cv2.cvtColor(kisi_bolgesi, cv2.COLOR_BGR2GRAY)
    yuzler = _dedektoru_al().detectMultiScale(gri, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))

    if len(yuzler) == 0:
        # Guvenlik agi: kisi kutusunun ust %25'i (bas/yuz bolgesinin genelde
        # bulundugu alan) blurlanir, boylece yuz tespiti kacirilsa bile
        # KVKK acisindan riskli bir fotograf disari cikmaz.
        genislik = x2 - x1
        ust_ceyrek_yuksekligi = max(1, (y2 - y1) // 4)
        _blur_uygula(blurlu, x1, y1, genislik, ust_ceyrek_yuksekligi)
        return blurlu

    for (fx, fy, fw, fh) in yuzler:
        # Bir miktar pay birakilir ki yuzun kenarlari (sac, cene) da ortulsun.
        pay_x, pay_y = int(fw * 0.2), int(fh * 0.2)
        _blur_uygula(
            blurlu,
            x1 + fx - pay_x,
            y1 + fy - pay_y,
            fw + 2 * pay_x,
            fh + 2 * pay_y,
        )

    return blurlu
