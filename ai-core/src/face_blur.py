"""
MODUL-1: KVKK — kanit karesindeki TUM kisilerin yuz/bas bolgesini sansurler.

Strateji (katmanli, kacirma riskini dusurur):
1) Verilen her kisi / ihlal kutusunun ust yarisi (bas) zorunlu blur
2) Tum karede frontal+profil Haar yuz tespiti → bulunan her yuz blur
3) Kutu icinde ek yuz tarama

BARET ve YELEK ayri kayit olsa bile ayni karedeki diger kisiler de blurlanir.
"""
from __future__ import annotations

import cv2
import numpy as np

_yuz_dedektoru: cv2.CascadeClassifier | None = None
_profil_dedektoru: cv2.CascadeClassifier | None = None


def _frontal_dedektor() -> cv2.CascadeClassifier:
    global _yuz_dedektoru
    if _yuz_dedektoru is None:
        yol = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _yuz_dedektoru = cv2.CascadeClassifier(yol)
    return _yuz_dedektoru


def _profil_dedektor() -> cv2.CascadeClassifier:
    global _profil_dedektoru
    if _profil_dedektoru is None:
        yol = cv2.data.haarcascades + "haarcascade_profileface.xml"
        _profil_dedektoru = cv2.CascadeClassifier(yol)
    return _profil_dedektoru


def _blur_uygula(kare: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    """Guclu gaussian + pixelate — kimlik tanima riskini azaltir."""
    x, y = max(0, x), max(0, y)
    x2, y2 = min(kare.shape[1], x + w), min(kare.shape[0], y + h)
    if x2 <= x or y2 <= y:
        return
    bolge = kare[y:y2, x:x2]
    bh, bw = bolge.shape[:2]
    if bh < 2 or bw < 2:
        return

    # Once kucuk cozunurluge indirip geri buyut (pixelate)
    kucuk_w = max(1, bw // 12)
    kucuk_h = max(1, bh // 12)
    kucuk = cv2.resize(bolge, (kucuk_w, kucuk_h), interpolation=cv2.INTER_LINEAR)
    pixelate = cv2.resize(kucuk, (bw, bh), interpolation=cv2.INTER_NEAREST)

    k = max(31, (min(bh, bw) // 2) | 1)
    kare[y:y2, x:x2] = cv2.GaussianBlur(pixelate, (k, k), 0)


def _bolgede_yuzleri_bul(gri: np.ndarray) -> list[tuple[int, int, int, int]]:
    if gri.size == 0 or gri.shape[0] < 10 or gri.shape[1] < 10:
        return []

    # Kontrast iyilestirme — santiye isiginda Haar daha iyi yakalar
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gelismis = clahe.apply(gri)

    parametreler_listesi = [
        dict(scaleFactor=1.05, minNeighbors=3, minSize=(16, 16)),
        dict(scaleFactor=1.1, minNeighbors=2, minSize=(12, 12)),
    ]

    yuzler: list[tuple[int, int, int, int]] = []
    genislik = gri.shape[1]

    for parametreler in parametreler_listesi:
        for kaynak in (gri, gelismis):
            frontal = _frontal_dedektor().detectMultiScale(kaynak, **parametreler)
            profil = _profil_dedektor().detectMultiScale(kaynak, **parametreler)
            aynali = cv2.flip(kaynak, 1)
            profil_aynali = _profil_dedektor().detectMultiScale(aynali, **parametreler)

            for (x, y, w, h) in list(frontal) + list(profil):
                yuzler.append((int(x), int(y), int(w), int(h)))
            for (x, y, w, h) in profil_aynali:
                yuzler.append((int(genislik - x - w), int(y), int(w), int(h)))

    return _kutulari_birlestir(yuzler)


def _kutulari_birlestir(
    kutular: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    """Cakisen yuz kutularini tekilleştir."""
    if not kutular:
        return []
    kutular = sorted(kutular, key=lambda k: k[2] * k[3], reverse=True)
    sonuc: list[tuple[int, int, int, int]] = []
    for x, y, w, h in kutular:
        cx, cy = x + w / 2, y + h / 2
        tekrar = False
        for sx, sy, sw, sh in sonuc:
            if sx <= cx <= sx + sw and sy <= cy <= sy + sh:
                tekrar = True
                break
        if not tekrar:
            sonuc.append((x, y, w, h))
    return sonuc


def _yuzu_payli_blurla(kare: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    pay_x, pay_y = int(w * 0.45), int(h * 0.45)
    _blur_uygula(kare, x - pay_x, y - pay_y, w + 2 * pay_x, h + 2 * pay_y)


def _kisi_bas_bolgesini_blurla(
    kare: np.ndarray, kisi_kutusu: tuple[int, int, int, int], oran: float = 0.55
) -> None:
    """Kisi kutusunun ust kismini (bas/yuz) zorunlu sansurle — Haar kacirsa bile."""
    x1, y1, x2, y2 = kisi_kutusu
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(kare.shape[1], x2), min(kare.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return
    genislik = x2 - x1
    yukseklik = y2 - y1
    bas_h = max(1, int(yukseklik * oran))
    # Biraz yana genislet
    pay = int(genislik * 0.08)
    _blur_uygula(kare, x1 - pay, y1, genislik + 2 * pay, bas_h)


def kanit_yuzlerini_blurla(
    kare: np.ndarray,
    kisi_kutulari: list[tuple[int, int, int, int]] | None = None,
) -> np.ndarray:
    """
    Kanit karesinin KVKK-uyumlu kopyasi: fotograftaki tum kisilerin yuzleri blurlu.
    """
    blurlu = kare.copy()
    gri = cv2.cvtColor(blurlu, cv2.COLOR_BGR2GRAY)

    benzersiz: list[tuple[int, int, int, int]] = []
    for kutu in kisi_kutulari or []:
        if kutu not in benzersiz:
            benzersiz.append(kutu)

    # 1) Her kisi / ihlal kutusu icin bas bolgesi ZORUNLU blur
    for kutu in benzersiz:
        _kisi_bas_bolgesini_blurla(blurlu, kutu, oran=0.55)

    # 2) Tum karede yuz tespiti
    for (x, y, w, h) in _bolgede_yuzleri_bul(gri):
        _yuzu_payli_blurla(blurlu, x, y, w, h)

    # 3) Her kutu icinde ek yuz tarama
    for kutu in benzersiz:
        x1, y1, x2, y2 = kutu
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(blurlu.shape[1], x2), min(blurlu.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            continue
        alt = gri[y1:y2, x1:x2]
        for (fx, fy, fw, fh) in _bolgede_yuzleri_bul(alt):
            _yuzu_payli_blurla(blurlu, x1 + fx, y1 + fy, fw, fh)

    return blurlu


def kisi_yuzunu_blurla(
    kare: np.ndarray, kisi_kutusu: tuple[int, int, int, int]
) -> np.ndarray:
    """Geriye donuk tek-kisi API'si."""
    return kanit_yuzlerini_blurla(kare, [kisi_kutusu])
