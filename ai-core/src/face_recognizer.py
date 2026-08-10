"""
Kisi tanima: OpenCV YuNet (tespit) + SFace (embedding).

Sifirdan egitim YOK. face_gallery/ klasorundeki referans yuz fotograflarindan
embedding uretilir; canli ihlal karesinde cosine benzerlik ile eslesme yapilir.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .face_models import yuz_model_yollari

logger = logging.getLogger(__name__)

# OpenCV SFace dokumantasyonu: cosine esik ~0.363
VARSAYILAN_COSINE_ESIK = 0.363
_FOTO_UZANTILARI = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class TaninanKisi:
    personel_id: int | None
    sicil_no: str
    ad_soyad: str
    skor: float


@dataclass
class _GaleriKayit:
    personel_id: int | None
    sicil_no: str
    ad_soyad: str
    embedding: np.ndarray


def _klasor_adindan_kimlik(klasor_adi: str) -> tuple[str, str]:
    """
    'P-1001_Ahmet_Yilmaz' -> ('P-1001', 'Ahmet Yilmaz')
    'P-1001' -> ('P-1001', 'P-1001')
    """
    ad = klasor_adi.strip()
    if "_" in ad:
        sicil, kalan = ad.split("_", 1)
        ad_soyad = kalan.replace("_", " ").strip() or sicil
        return sicil.strip(), ad_soyad
    return ad, ad


class YuzTanima:
    """Galeri yukler, karedeki kisi kutusundan yuzu tanir."""

    def __init__(
        self,
        models_dir,
        *,
        cosine_esik: float = VARSAYILAN_COSINE_ESIK,
        etkin: bool = True,
    ):
        self._etkin = etkin
        self._cosine_esik = float(cosine_esik)
        self._dedektor = None
        self._taniyici = None
        self._galeri: list[_GaleriKayit] = []
        self._models_dir = models_dir

        if not etkin:
            logger.info("Kisi tanima kapali (FACE_RECOGNITION_ENABLED=false)")
            return

        try:
            yunet, sface = yuz_model_yollari(models_dir)
            self._dedektor = cv2.FaceDetectorYN.create(
                str(yunet), "", (320, 320), 0.7, 0.3, 5000
            )
            self._taniyici = cv2.FaceRecognizerSF.create(str(sface), "")
            logger.info("Kisi tanima modelleri hazir (YuNet + SFace)")
        except Exception:
            logger.exception(
                "Kisi tanima modelleri yuklenemedi; tanima devre disi. "
                "Internet ile models/ altina ONNX indirilebilmeli."
            )
            self._etkin = False
            self._dedektor = None
            self._taniyici = None

    @property
    def hazir_mi(self) -> bool:
        return self._etkin and self._dedektor is not None and self._taniyici is not None

    @property
    def galeri_kisi_sayisi(self) -> int:
        return len({g.sicil_no for g in self._galeri})

    def klasorden_yukle(self, galeri_dizini: Path) -> None:
        """
        face_gallery yapisi:

            face_gallery/
              P-1001_Ahmet_Yilmaz/
                1.jpg
                2.jpg
              P-1002_Mehmet_Demir/
                1.jpg

        Her alt klasor = bir kisi. Klasor adi: SICIL veya SICIL_Ad_Soyad.
        Kisi basina 1-5 net yuz fotografi onerilir.
        """
        if not self.hazir_mi:
            self._galeri = []
            return

        kok = Path(galeri_dizini)
        if not kok.is_dir():
            logger.warning("Yuz galeri klasoru yok: %s", kok)
            self._galeri = []
            return

        yeni: list[_GaleriKayit] = []
        for alt in sorted(kok.iterdir()):
            if not alt.is_dir() or alt.name.startswith("."):
                continue
            sicil, ad_soyad = _klasor_adindan_kimlik(alt.name)
            if not sicil:
                continue
            fotolar = [
                p
                for p in sorted(alt.iterdir())
                if p.is_file() and p.suffix.lower() in _FOTO_UZANTILARI
            ]
            if not fotolar:
                logger.warning("Galeri klasorunde foto yok, atlandi: %s", alt.name)
                continue
            for foto in fotolar:
                emb = self._dosya_embedding(foto)
                if emb is None:
                    logger.warning("Yuz cikarilamadi, atlandi: %s", foto)
                    continue
                yeni.append(
                    _GaleriKayit(
                        personel_id=None,
                        sicil_no=sicil,
                        ad_soyad=ad_soyad,
                        embedding=emb,
                    )
                )

        # Duz dosya formati (opsiyonel): P-1001_Ahmet.jpg
        for foto in sorted(kok.iterdir()):
            if not foto.is_file() or foto.suffix.lower() not in _FOTO_UZANTILARI:
                continue
            stem = foto.stem
            m = re.match(r"^(P-?\d+|[A-Za-z0-9-]+)(?:_(.+))?$", stem)
            if not m:
                continue
            sicil = m.group(1)
            ad_soyad = (m.group(2) or sicil).replace("_", " ")
            emb = self._dosya_embedding(foto)
            if emb is None:
                logger.warning("Yuz cikarilamadi, atlandi: %s", foto)
                continue
            yeni.append(
                _GaleriKayit(
                    personel_id=None,
                    sicil_no=sicil,
                    ad_soyad=ad_soyad,
                    embedding=emb,
                )
            )

        self._galeri = yeni
        logger.info(
            "Yuz galerisi (klasor) yuklendi: %s embedding, %s kisi (%s)",
            len(self._galeri),
            self.galeri_kisi_sayisi,
            kok,
        )

    def tani(
        self,
        kare: np.ndarray,
        kisi_kutusu: tuple[int, int, int, int] | None = None,
    ) -> TaninanKisi | None:
        if not self.hazir_mi or not self._galeri or kare is None or kare.size == 0:
            return None

        yuz_kutusu = self._yuz_bul(kare, kisi_kutusu)
        if yuz_kutusu is None:
            return None

        emb = self._yuz_embedding(kare, yuz_kutusu)
        if emb is None:
            return None

        en_iyi: _GaleriKayit | None = None
        en_iyi_skor = -1.0
        for kayit in self._galeri:
            skor = float(
                self._taniyici.match(
                    emb, kayit.embedding, cv2.FaceRecognizerSF_FR_COSINE
                )
            )
            if skor > en_iyi_skor:
                en_iyi_skor = skor
                en_iyi = kayit

        if en_iyi is None or en_iyi_skor < self._cosine_esik:
            logger.debug(
                "Yuz eslesmedi (en_iyi=%.3f esik=%.3f)",
                en_iyi_skor,
                self._cosine_esik,
            )
            return None

        return TaninanKisi(
            personel_id=en_iyi.personel_id,
            sicil_no=en_iyi.sicil_no,
            ad_soyad=en_iyi.ad_soyad,
            skor=en_iyi_skor,
        )

    def _dosya_embedding(self, yol: Path) -> np.ndarray | None:
        img = _imread_unicode(yol)
        if img is None:
            return None
        yuz = self._yuz_bul(img, None)
        if yuz is None:
            yuz = self._sentetik_yuz_kutusu(img.shape[1], img.shape[0])
        return self._yuz_embedding(img, yuz)

    @staticmethod
    def _sentetik_yuz_kutusu(genislik: int, yukseklik: int) -> np.ndarray:
        w, h = float(genislik), float(yukseklik)
        return np.array(
            [
                0.0,
                0.0,
                w,
                h,
                0.30 * w,
                0.35 * h,
                0.70 * w,
                0.35 * h,
                0.50 * w,
                0.52 * h,
                0.35 * w,
                0.72 * h,
                0.65 * w,
                0.72 * h,
                0.90,
            ],
            dtype=np.float32,
        )

    def _yuz_bul(
        self,
        kare: np.ndarray,
        kisi_kutusu: tuple[int, int, int, int] | None,
    ) -> np.ndarray | None:
        assert self._dedektor is not None
        h, w = kare.shape[:2]
        if kisi_kutusu is not None:
            x1, y1, x2, y2 = kisi_kutusu
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            y2 = y1 + max(1, int((y2 - y1) * 0.75))
            if x2 - x1 < 20 or y2 - y1 < 20:
                return None
            roi = kare[y1:y2, x1:x2]
            ox, oy = x1, y1
        else:
            roi = kare
            ox, oy = 0, 0

        rh, rw = roi.shape[:2]
        self._dedektor.setInputSize((rw, rh))
        _, yuzler = self._dedektor.detect(roi)
        if yuzler is None or len(yuzler) == 0:
            return None

        en_iyi = max(yuzler, key=lambda f: float(f[-1]))
        sonuc = en_iyi.copy()
        sonuc[0] += ox
        sonuc[1] += oy
        for i in range(4, 14, 2):
            sonuc[i] += ox
            sonuc[i + 1] += oy
        return sonuc

    def _yuz_embedding(self, kare: np.ndarray, yuz_kutusu: np.ndarray) -> np.ndarray | None:
        assert self._taniyici is not None
        try:
            hizali = self._taniyici.alignCrop(kare, yuz_kutusu)
            return self._taniyici.feature(hizali)
        except Exception:
            logger.debug("Embedding cikarilamadi", exc_info=True)
            return None


def _imread_unicode(yol: Path) -> np.ndarray | None:
    """
    Windows'ta cv2.imread Turkce karakterli yollari (Sıla vb.) acamaz.
    np.fromfile + imdecode ile Unicode-guvenli okuma yapilir.
    """
    try:
        veri = np.fromfile(str(yol), dtype=np.uint8)
        if veri.size == 0:
            return None
        return cv2.imdecode(veri, cv2.IMREAD_COLOR)
    except Exception:
        return None
