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
"person" sinifini tespit ederek DEMO_MODU'nda calisir: bu modda tespit
edilen her insan, boru hattinin (yakalama + backend POST) uctan uca
dogrulanabilmesi icin BUTUN ihlal tipleriyle isaretlenir. Bu GERCEK BIR
URETIM TESPITI DEGILDIR; yalnizca gelistirme/kalibrasyon icindir ve
baslangicta acikca loglanir (bkz. README.md "PPE modeli" bolumu).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

from .config import Ayarlar

logger = logging.getLogger(__name__)

# Yaygin PPE veri kumelerindeki "eksik ekipman" siniflarinin ihlal tipine
# eslestirilmesi. Model bu isimlerden hicbirini icermiyorsa DEMO_MODU'na
# dusulur (bkz. PpeDedektoru.__init__).
SINIF_TO_IHLAL_TIPI: dict[str, str] = {
    "NO-Hardhat": "BARET",
    "NO-Helmet": "BARET",
    "NO-Safety Vest": "YELEK",
    "NO-Vest": "YELEK",
    "NO-Goggles": "GOZLUK",
    "NO-Glasses": "GOZLUK",
}

TUM_IHLAL_TIPLERI = ("BARET", "YELEK", "GOZLUK")

# Kisi sinifi: COCO modellerinde "person", Construction Site Safety
# (Roboflow) PPE modellerinde genelde "Person" olarak gelir.
KISI_SINIF_ISIMLERI = frozenset({"person", "Person"})


@dataclass(frozen=True)
class Ihlal:
    ihlal_tipi_adi: str
    guven: float
    kisi_kutusu: tuple[int, int, int, int]  # x1, y1, x2, y2


class PpeDedektoru:
    def __init__(self, ayarlar: Ayarlar):
        self._ayarlar = ayarlar

        if ayarlar.yolo_model_yolu.exists():
            logger.info("PPE modeli yukleniyor: %s", ayarlar.yolo_model_yolu)
            self._model = YOLO(str(ayarlar.yolo_model_yolu))
        else:
            logger.warning(
                "PPE modeli bulunamadi (%s). Genel amacli 'yolov8n.pt' (COCO) "
                "modeline dusuluyor ve DEMO_MODU aktif ediliyor: bu modda "
                "sadece 'person' sinifi tespit edilir ve GERCEK BIR IHLAL "
                "TESPITI YAPILMAZ; boru hatti (yakalama->backend POST) "
                "test/kalibrasyon amaciyla simule edilir. Uretimde "
                "models/ppe_yolov8n.pt yerine gercek bir PPE modeli koyunuz "
                "(bkz. ai-core/README.md).",
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

    def tespit_et(self, kare: np.ndarray) -> list[Ihlal]:
        """Karedeki KDD ihlallerini dondurur."""
        sonuclar = self._model.predict(
            kare, conf=self._ayarlar.guven_esigi, verbose=False
        )
        if not sonuclar:
            return []

        kutular = sonuclar[0].boxes
        if kutular is None or len(kutular) == 0:
            return []

        etiketli_kutular = []
        for kutu in kutular:
            sinif_id = int(kutu.cls[0])
            sinif_adi = self._sinif_isimleri.get(sinif_id, "")
            guven = float(kutu.conf[0])
            x1, y1, x2, y2 = (int(v) for v in kutu.xyxy[0])
            etiketli_kutular.append((sinif_adi, guven, (x1, y1, x2, y2)))

        if self._demo_modu:
            return self._demo_ihlalleri_uret(etiketli_kutular)
        return self._gercek_ihlalleri_uret(etiketli_kutular)

    def _gercek_ihlalleri_uret(self, etiketli_kutular) -> list[Ihlal]:
        kisiler = [kb for kb in etiketli_kutular if kb[0] in KISI_SINIF_ISIMLERI]
        ihlaller: list[Ihlal] = []
        for sinif_adi, guven, kutu in etiketli_kutular:
            ihlal_tipi = SINIF_TO_IHLAL_TIPI.get(sinif_adi)
            if ihlal_tipi is None:
                continue
            kisi_kutusu = _en_yakin_kisi_kutusu(kutu, kisiler) or kutu
            ihlaller.append(Ihlal(ihlal_tipi, guven, kisi_kutusu))
        return ihlaller

    def _demo_ihlalleri_uret(self, etiketli_kutular) -> list[Ihlal]:
        """DEMO_MODU: her tespit edilen kisi, boru hattini test edebilmek
        icin butun ihlal tipleriyle isaretlenir (gercek tespit degildir)."""
        ihlaller: list[Ihlal] = []
        for sinif_adi, guven, kutu in etiketli_kutular:
            if sinif_adi not in KISI_SINIF_ISIMLERI:
                continue
            for ihlal_tipi in TUM_IHLAL_TIPLERI:
                ihlaller.append(Ihlal(ihlal_tipi, guven, kutu))
        return ihlaller


def _en_yakin_kisi_kutusu(hedef_kutu, kisi_kutulari):
    """Bir KDD-eksik kutusunu (ör. NO-Hardhat), merkez mesafesine gore en
    yakin kisi kutusuyla iliskilendirir."""
    if not kisi_kutulari:
        return None

    def merkez(kutu):
        x1, y1, x2, y2 = kutu
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    hx, hy = merkez(hedef_kutu)
    en_yakin = min(
        kisi_kutulari,
        key=lambda kb: (merkez(kb[2])[0] - hx) ** 2 + (merkez(kb[2])[1] - hy) ** 2,
    )
    return en_yakin[2]
