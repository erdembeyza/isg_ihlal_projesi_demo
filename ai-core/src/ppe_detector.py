"""
MODUL-1 (tasarim_mimari.md): YOLOv8 Nano tabanli KDD (baret/yelek/gozluk)
ihlal tespit motoru.

Gercek bir PPE (Personal Protective Equipment) modeli egitilip
`YOLO_MODEL_PATH` (varsayilan: models/ppe_yolov8n.pt) konumuna
yerlestirildiginde, bu modul o modelin sinif isimlerini asagidaki
SINIF_TO_IHLAL_TIPI sozlugu araciligiyla ihlal tipine (BARET/YELEK/GOZLUK)
cevirir. Sinif isimlendirmesi, bu alanda yaygin kullanilan acik kaynak
"Construction Site Safety" (Roboflow/Kaggle) veri kumesindeki NO-Hardhat /
NO-Safety Vest kaliplarini esas alir.

PPE modeli henuz mevcut degilse (dosya bulunamazsa), ultralytics'in COCO
uzerinde on-egitilmis genel amacli `yolov8n.pt` modeline duser ve yalnizca
"person" sinifini tespit ederek DEMO_MODU'nda calisir.
"""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

from .config import Ayarlar
from .tracker import kutu_iou

logger = logging.getLogger(__name__)

SINIF_TO_IHLAL_TIPI: dict[str, str] = {
    "NO-Hardhat": "BARET",
    "NO-Helmet": "BARET",
    "NO-Safety Vest": "YELEK",
    "NO-Vest": "YELEK",
    "NO-Goggles": "GOZLUK",
    "NO-Glasses": "GOZLUK",
}

TUM_IHLAL_TIPLERI = ("BARET", "YELEK", "GOZLUK")

KISI_SINIF_ISIMLERI = frozenset({"person", "Person"})

# PPE kutusu bir kisiye bu kadar yakin/ortusmeli; aksi halde masa vb. false-positive sayilir.
_MIN_PPE_KISI_IOU = 0.02
_MAX_MERKEZ_ORAN = 0.55  # kisi kosegenine gore


# YOLO kisi kutusu siklikla tepayi (kafa/baret) keser; cizimde uste pay birak.
_CIZIM_UST_ORAN = 0.16
_CIZIM_YAN_ORAN = 0.06


def kisi_cizim_kutusunu_genislet(
    kutu: tuple[int, int, int, int],
    *,
    kare_boyutu: tuple[int, int] | None = None,
    ppe_kutu: tuple[int, int, int, int] | None = None,
) -> tuple[int, int, int, int]:
    """
    Kirmizi cerceve icin kisi kutusunu genisletir (ozellikle kafa ustu).
    Takip (kisi_kutusu) degismez; yalnizca gorsel/kanit cizimi icin.
    """
    x1, y1, x2, y2 = kutu
    h = max(1, y2 - y1)
    w = max(1, x2 - x1)
    nx1 = x1 - int(w * _CIZIM_YAN_ORAN)
    ny1 = y1 - int(h * _CIZIM_UST_ORAN)
    nx2 = x2 + int(w * _CIZIM_YAN_ORAN)
    ny2 = y2

    # BARET vb. PPE kutusu kafanin ustune tasiyorsa onu da kapsa.
    if ppe_kutu is not None:
        px1, py1, px2, py2 = ppe_kutu
        nx1 = min(nx1, px1)
        ny1 = min(ny1, py1)
        nx2 = max(nx2, px2)
        # PPE altini zorla genisletme (yelek kutusu tum govdeyi kaplamasin)
        _ = py2

    if kare_boyutu is not None:
        kh, kw = kare_boyutu
        nx1 = max(0, nx1)
        ny1 = max(0, ny1)
        nx2 = min(kw - 1, nx2)
        ny2 = min(kh - 1, ny2)
    else:
        nx1 = max(0, nx1)
        ny1 = max(0, ny1)

    return nx1, ny1, nx2, ny2


@dataclass(frozen=True)
class Ihlal:
    ihlal_tipi_adi: str
    guven: float
    kisi_kutusu: tuple[int, int, int, int]  # x1,y1,x2,y2 — takip (kisi)
    cizim_kutusu: tuple[int, int, int, int] | None = None

    def kutu_cizim_icin(self) -> tuple[int, int, int, int]:
        """Dikdortgen kisi uzerinde; mumkunse genisletilmis cizim kutusu."""
        return self.cizim_kutusu or self.kisi_kutusu


class PpeDedektoru:
    def __init__(self, ayarlar: Ayarlar):
        self._ayarlar = ayarlar
        self._inferans_kilidi = threading.Lock()

        if ayarlar.yolo_model_yolu.exists():
            logger.info("PPE modeli yukleniyor: %s", ayarlar.yolo_model_yolu)
            self._model = YOLO(str(ayarlar.yolo_model_yolu))
        else:
            logger.warning(
                "PPE modeli bulunamadi (%s). Genel amacli 'yolov8n.pt' (COCO) "
                "modeline dusuluyor ve DEMO_MODU aktif ediliyor.",
                ayarlar.yolo_model_yolu,
            )
            self._model = YOLO("yolov8n.pt")

        self._sinif_isimleri: dict[int, str] = self._model.names
        self._demo_modu = not (set(self._sinif_isimleri.values()) & SINIF_TO_IHLAL_TIPI.keys())

        if self._demo_modu and not (set(self._sinif_isimleri.values()) & KISI_SINIF_ISIMLERI):
            raise RuntimeError(
                "Yuklenen modelde ne PPE ihlal siniflari ne de kisi "
                "sinifi (person/Person) bulundu; bu model AI Core ile uyumlu degil."
            )

    @property
    def demo_modu_mu(self) -> bool:
        return self._demo_modu

    def _etiketli_kutulari_al(
        self, kare: np.ndarray
    ) -> list[tuple[str, float, tuple[int, int, int, int]]]:
        with self._inferans_kilidi:
            sonuclar = self._model.predict(
                kare, conf=self._ayarlar.guven_esigi, verbose=False
            )
        if not sonuclar:
            return []

        kutular = sonuclar[0].boxes
        if kutular is None or len(kutular) == 0:
            return []

        etiketli_kutular: list[tuple[str, float, tuple[int, int, int, int]]] = []
        for kutu in kutular:
            sinif_id = int(kutu.cls[0])
            sinif_adi = self._sinif_isimleri.get(sinif_id, "")
            guven = float(kutu.conf[0])
            x1, y1, x2, y2 = (int(v) for v in kutu.xyxy[0])
            etiketli_kutular.append((sinif_adi, guven, (x1, y1, x2, y2)))
        return etiketli_kutular

    def tespit_et(self, kare: np.ndarray) -> list[Ihlal]:
        """Karedeki KDD ihlallerini dondurur (yalnizca kisiye bagli PPE)."""
        etiketli_kutular = self._etiketli_kutulari_al(kare)
        if not etiketli_kutular:
            return []
        if self._demo_modu:
            return self._demo_ihlalleri_uret(etiketli_kutular)
        return self._gercek_ihlalleri_uret(etiketli_kutular)

    def kisi_kutularini_bul(
        self, kare: np.ndarray
    ) -> list[tuple[int, int, int, int]]:
        """Karedeki tum kisi kutularini dondurur (yuz blur icin)."""
        etiketli = self._etiketli_kutulari_al(kare)
        return [kutu for sinif, _, kutu in etiketli if sinif in KISI_SINIF_ISIMLERI]

    def _gercek_ihlalleri_uret(self, etiketli_kutular) -> list[Ihlal]:
        kisiler = [kb for kb in etiketli_kutular if kb[0] in KISI_SINIF_ISIMLERI]
        ihlaller: list[Ihlal] = []
        for sinif_adi, guven, ppe_kutu in etiketli_kutular:
            ihlal_tipi = SINIF_TO_IHLAL_TIPI.get(sinif_adi)
            if ihlal_tipi is None:
                continue
            kisi_kutusu = _ppe_yi_kisiye_bagla(ppe_kutu, kisiler)
            if kisi_kutusu is None:
                # Masa/kutu vb. false-positive — kisi yoksa ihlal sayma.
                continue
            cizim = kisi_cizim_kutusunu_genislet(
                kisi_kutusu,
                ppe_kutu=ppe_kutu if ihlal_tipi == "BARET" else None,
            )
            ihlaller.append(
                Ihlal(
                    ihlal_tipi,
                    guven,
                    kisi_kutusu,
                    cizim_kutusu=cizim,
                )
            )
        return ihlaller

    def _demo_ihlalleri_uret(self, etiketli_kutular) -> list[Ihlal]:
        ihlaller: list[Ihlal] = []
        for sinif_adi, guven, kutu in etiketli_kutular:
            if sinif_adi not in KISI_SINIF_ISIMLERI:
                continue
            cizim = kisi_cizim_kutusunu_genislet(kutu)
            for ihlal_tipi in TUM_IHLAL_TIPLERI:
                ihlaller.append(Ihlal(ihlal_tipi, guven, kutu, cizim_kutusu=cizim))
        return ihlaller


def _merkez(kutu: tuple[int, int, int, int]) -> tuple[float, float]:
    x1, y1, x2, y2 = kutu
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def _nokta_kutu_icinde(x: float, y: float, kutu: tuple[int, int, int, int]) -> bool:
    x1, y1, x2, y2 = kutu
    return x1 <= x <= x2 and y1 <= y <= y2


def _ppe_yi_kisiye_bagla(
    ppe_kutu: tuple[int, int, int, int],
    kisi_kutulari: list[tuple[str, float, tuple[int, int, int, int]]],
) -> tuple[int, int, int, int] | None:
    """
    PPE tespitini bir kisi kutusuyla eslestirir.
    Eslesme yoksa None (masa/nesne false-positive elenir).
    """
    if not kisi_kutulari:
        return None

    px, py = _merkez(ppe_kutu)

    # 1) PPE merkezi kisi kutusu icindeyse — en guvenilir
    icindekiler = [
        kutu for _, _, kutu in kisi_kutulari if _nokta_kutu_icinde(px, py, kutu)
    ]
    if icindekiler:
        # En kucuk kapsayan kisi (yanlis komsuya gitmesin)
        return min(icindekiler, key=lambda k: (k[2] - k[0]) * (k[3] - k[1]))

    # 2) IoU ile ortusen kisi
    en_iyi_iou = 0.0
    en_iyi_kutu: tuple[int, int, int, int] | None = None
    for _, _, kutu in kisi_kutulari:
        iou = kutu_iou(ppe_kutu, kutu)
        if iou > en_iyi_iou:
            en_iyi_iou = iou
            en_iyi_kutu = kutu
    if en_iyi_kutu is not None and en_iyi_iou >= _MIN_PPE_KISI_IOU:
        return en_iyi_kutu

    # 3) Merkez mesafesi (kisi kosegenine oranla)
    en_iyi_skor = float("inf")
    en_yakin: tuple[int, int, int, int] | None = None
    for _, _, kutu in kisi_kutulari:
        kx, ky = _merkez(kutu)
        kosegen = max(1.0, ((kutu[2] - kutu[0]) ** 2 + (kutu[3] - kutu[1]) ** 2) ** 0.5)
        uzaklik = ((px - kx) ** 2 + (py - ky) ** 2) ** 0.5
        oran = uzaklik / kosegen
        if oran < en_iyi_skor:
            en_iyi_skor = oran
            en_yakin = kutu
    if en_yakin is not None and en_iyi_skor <= _MAX_MERKEZ_ORAN:
        return en_yakin

    return None
