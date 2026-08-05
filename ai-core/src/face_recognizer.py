"""
Multi-Shot Yüz Tanıma Modülü.

Mimari:
  - reference_faces/ klasöründeki dosyaları okur.
  - Dosya adından '_N' suffix'ini Regex ile kırparak etiketi (kişi adını) çıkarır.
    Örn: 'Beyza_Erdem_2.jpeg'  → etiket: 'Beyza_Erdem'
         'Sıla_Sibirli.jpeg'   → etiket: 'Sıla_Sibirli'  (numera yoksa olduğu gibi)
  - Her fotoğraf için 128-boyutlu dlib embedding'i hesaplar.
  - Aynı etikete ait embedding'leri bir listede tutar (Multi-Shot cache).

Eşleştirme (Minimum Mesafe / K-NN):
  - Canlı yüz embedding'i, her referans embedding ile ayrı ayrı karşılaştırılır.
  - Kişi başına en küçük Öklid mesafesi alınır.
  - Global minimum, eşiğin altındaysa o kişinin kimliği döndürülür; üstündeyse
    'Bilinmeyen' döndürülür.

Neden Minimum Mesafe?
  - Average Embedding, kötü açılı / gürültülü bir fotoğraf eklendiğinde
    ortalamayı bozabilir. Minimum mesafe, her referansı bağımsız değerlendirerek
    aydınlatma ve poz farklılıklarına karşı daha dayanıklı sonuç verir.
"""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Desteklenen uzantılar (küçük harf karşılaştırması yapılır)
_DESTEKLENEN_UZANTILAR = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Dosya adı suffix Regex: '_' ardından bir veya daha fazla rakam, uzantıdan önce.
# Örn: 'Beyza_Erdem_2' → grup 'Beyza_Erdem'
_SUFFIX_REGEX = re.compile(r"^(.+?)_\d+$")


def _etiketi_cikar(dosya_adi_gövdesi: str) -> str:
    """
    Dosya adı gövdesinden (uzantısız) kişi etiketini çıkarır.

    'Beyza_Erdem_1'  → 'Beyza_Erdem'
    'Sıla_Sibirli'   → 'Sıla_Sibirli'   (numara yoksa değişmez)
    """
    eslesme = _SUFFIX_REGEX.match(dosya_adi_gövdesi)
    return eslesme.group(1) if eslesme else dosya_adi_gövdesi


class YuzTaniyici:
    """
    Multi-Shot yüz tanıma motoru.

    Parametreler
    ------------
    reference_faces_klasoru : Path
        Referans yüz fotoğraflarının bulunduğu klasör.
    esik : float
        Öklid mesafesi eşiği. Bu değerin altındaki mesafeler 'tanındı' olarak
        işaretlenir. Önerilen aralık: 0.45–0.55 (dlib 128-d modelinde).
    """

    def __init__(self, reference_faces_klasoru: Path, esik: float = 0.50) -> None:
        self._esik = esik
        # {etiket: [embedding, ...]}
        self._referans_embeddingler: dict[str, list[np.ndarray]] = {}
        self._yuklendi = False

        try:
            import face_recognition  # noqa: F401 — import testi
            self._face_recognition = face_recognition
        except ImportError:
            logger.error(
                "face_recognition kütüphanesi bulunamadı. "
                "Kurulum: pip install face_recognition  "
                "(dlib önceden kurulu olmalı; bkz. ai-core/README.md)"
            )
            self._face_recognition = None
            return

        self._referans_embeddingler = self._klasoru_yukle(reference_faces_klasoru)
        self._yuklendi = True
        kisi_sayisi = len(self._referans_embeddingler)
        toplam_fotograf = sum(len(v) for v in self._referans_embeddingler.values())
        logger.info(
            "Yüz Tanıma: %d kişi, %d referans fotoğraf yüklendi. Eşik=%.2f",
            kisi_sayisi,
            toplam_fotograf,
            esik,
        )

    # ------------------------------------------------------------------
    # Referans klasörü yükleme
    # ------------------------------------------------------------------

    def _klasoru_yukle(
        self, klasor: Path
    ) -> dict[str, list[np.ndarray]]:
        """Klasördeki tüm uyumlu fotoğrafları okuyup embedding'lerini hesaplar."""
        if not klasor.is_dir():
            logger.warning(
                "reference_faces klasörü bulunamadı: %s  — Yüz tanıma devre dışı.", klasor
            )
            return {}

        # etiket → embedding listesi
        gruplar: dict[str, list[np.ndarray]] = defaultdict(list)
        yuklenen, atlanan = 0, 0

        for dosya in sorted(klasor.iterdir()):
            if dosya.suffix.lower() not in _DESTEKLENEN_UZANTILAR:
                continue

            etiket = _etiketi_cikar(dosya.stem)
            embedding = self._dosyadan_embedding_cikart(dosya)

            if embedding is not None:
                gruplar[etiket].append(embedding)
                yuklenen += 1
                logger.debug("  [✓] %s → etiket='%s'", dosya.name, etiket)
            else:
                atlanan += 1
                logger.warning(
                    "  [✗] %s — bu fotoğrafta yüz algılanamadı, atlanıyor.", dosya.name
                )

        if atlanan > 0:
            logger.warning(
                "%d referans fotoğrafta yüz tespit edilemedi (yukarıda listelendi).",
                atlanan,
            )

        return dict(gruplar)

    def _dosyadan_embedding_cikart(self, dosya_yolu: Path) -> np.ndarray | None:
        """
        Tek bir fotoğraftan 128-d embedding çıkarır.
        Fotoğrafta yüz bulunamazsa None döner.
        """
        fr = self._face_recognition
        try:
            goruntu = fr.load_image_file(str(dosya_yolu))
            embeddingler = fr.face_encodings(goruntu)
            if not embeddingler:
                return None
            if len(embeddingler) > 1:
                logger.debug(
                    "%s içinde %d yüz bulundu; yalnızca ilki kullanılıyor.",
                    dosya_yolu.name,
                    len(embeddingler),
                )
            return embeddingler[0]
        except Exception:
            logger.exception("%s yüklenirken hata oluştu.", dosya_yolu)
            return None

    # ------------------------------------------------------------------
    # Kamuya açık API
    # ------------------------------------------------------------------

    @property
    def hazir_mi(self) -> bool:
        """Yüz tanıma kütüphanesi yüklü ve en az 1 referans kişi tanımlıysa True."""
        return self._yuklendi and bool(self._referans_embeddingler)

    def tani(self, kare_bolgesi: np.ndarray) -> str:
        """
        Verilen görüntü bölgesindeki (kişi kutusu crop'u) yüzü tanır.

        Dönüş değeri
        ------------
        str
            Eşleşen kişi etiketi ('Beyza_Erdem') ya da 'Bilinmeyen'.
        """
        if not self.hazir_mi:
            return "Bilinmeyen"

        fr = self._face_recognition
        try:
            # RGB'ye çevir (OpenCV BGR → RGB)
            rgb = kare_bolgesi[:, :, ::-1]
            canli_embeddingler = fr.face_encodings(rgb)
            if not canli_embeddingler:
                return "Bilinmeyen"
            canli_emb = canli_embeddingler[0]
        except Exception:
            logger.exception("Canlı yüz embedding çıkarımı başarısız.")
            return "Bilinmeyen"

        return self._minimum_mesafe_ile_esles(canli_emb)

    def tani_tam_kare(self, kare: np.ndarray) -> list[tuple[str, tuple[int, int, int, int]]]:
        """
        Tam karedeki tüm yüzleri tespit edip tanır.

        Dönüş değeri
        ------------
        list of (etiket, (x1, y1, x2, y2))
            Her tanınan (veya 'Bilinmeyen') yüz için etiket + kutu çifti.
        """
        if not self.hazir_mi:
            return []

        fr = self._face_recognition
        try:
            rgb = kare[:, :, ::-1]
            konumlar = fr.face_locations(rgb, model="hog")   # hızlı CPU modeli
            embeddingler = fr.face_encodings(rgb, konumlar)
        except Exception:
            logger.exception("Tam kare yüz tespiti başarısız.")
            return []

        sonuclar: list[tuple[str, tuple[int, int, int, int]]] = []
        for emb, (ust, sag, alt, sol) in zip(embeddingler, konumlar):
            etiket = self._minimum_mesafe_ile_esles(emb)
            # face_recognition: (top, right, bottom, left) → bizim (x1,y1,x2,y2)
            kutu = (sol, ust, sag, alt)
            sonuclar.append((etiket, kutu))

        return sonuclar

    # ------------------------------------------------------------------
    # İç yardımcılar
    # ------------------------------------------------------------------

    def _minimum_mesafe_ile_esles(self, canli_emb: np.ndarray) -> str:
        """
        Minimum Mesafe (K-NN) algoritması:
          - Tüm referans vektörlerle Öklid mesafesi hesaplar.
          - Kişi başına en küçük mesafeyi seçer.
          - Global en küçük mesafe eşiğin altındaysa o kişiyi döndürür.

        Neden bu yaklaşım?
          face_recognition.compare_faces zaten Öklid < 0.6 kontrollü K-NN yapar,
          ancak biz kişi başına granüler minimum istiyoruz (Multi-Shot için kritik).
        """
        en_iyi_etiket = "Bilinmeyen"
        en_iyi_mesafe = float("inf")

        for etiket, referans_listesi in self._referans_embeddingler.items():
            if not referans_listesi:
                continue
            # Bu kişiye ait tüm referanslarla mesafe → en küçüğü al
            mesafeler = np.linalg.norm(
                np.array(referans_listesi) - canli_emb, axis=1
            )
            kisi_min_mesafe = float(np.min(mesafeler))

            if kisi_min_mesafe < en_iyi_mesafe:
                en_iyi_mesafe = kisi_min_mesafe
                en_iyi_etiket = etiket

        if en_iyi_mesafe <= self._esik:
            logger.debug(
                "Yüz eşleşti: '%s' (mesafe=%.4f ≤ eşik=%.2f)",
                en_iyi_etiket,
                en_iyi_mesafe,
                self._esik,
            )
            return en_iyi_etiket

        logger.debug(
            "Yüz tanınamadı — en yakın: '%s' (mesafe=%.4f > eşik=%.2f)",
            en_iyi_etiket,
            en_iyi_mesafe,
            self._esik,
        )
        return "Bilinmeyen"
