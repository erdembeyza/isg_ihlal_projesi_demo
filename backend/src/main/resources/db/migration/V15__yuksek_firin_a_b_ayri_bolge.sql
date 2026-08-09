-- Yuksek Firin A / B ayri bolgeler + formen coklu bolge (kullanici_bolgeler)
-- Beklenen id'ler (V14 sonrasi): A=4 (eski 'Yuksek Firin'), B=5

-- 1) A bolgesi: V14'teki tek 'Yuksek Firin' kaydini yeniden adlandir (veya yoksa ekle)
UPDATE bolgeler
SET bolge_adi = 'Yuksek Firin A Bolgesi',
    aciklama = 'Yuksek firin A bolgesi kamerasi (video ile canli simulasyon)'
WHERE bolge_adi = 'Yuksek Firin';

INSERT INTO bolgeler (bolge_adi, aciklama)
SELECT 'Yuksek Firin A Bolgesi', 'Yuksek firin A bolgesi kamerasi (video ile canli simulasyon)'
WHERE NOT EXISTS (SELECT 1 FROM bolgeler WHERE bolge_adi = 'Yuksek Firin A Bolgesi');

INSERT INTO bolgeler (bolge_adi, aciklama)
SELECT 'Yuksek Firin B Bolgesi', 'Yuksek firin B bolgesi kamerasi (video ile canli simulasyon)'
WHERE NOT EXISTS (SELECT 1 FROM bolgeler WHERE bolge_adi = 'Yuksek Firin B Bolgesi');

-- 2) Coklu bolge baglantisi
CREATE TABLE IF NOT EXISTS kullanici_bolgeler (
    kullanici_id BIGINT NOT NULL,
    bolge_id     BIGINT NOT NULL,
    CONSTRAINT pk_kullanici_bolgeler PRIMARY KEY (kullanici_id, bolge_id),
    CONSTRAINT fk_kb_kullanici FOREIGN KEY (kullanici_id)
        REFERENCES kullanicilar (id) ON DELETE CASCADE,
    CONSTRAINT fk_kb_bolge FOREIGN KEY (bolge_id)
        REFERENCES bolgeler (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kullanici_bolgeler_bolge_id ON kullanici_bolgeler (bolge_id);

-- Mevcut tek bolge_id kayitlarini aktar
INSERT INTO kullanici_bolgeler (kullanici_id, bolge_id)
SELECT k.id, k.bolge_id
FROM kullanicilar k
WHERE k.bolge_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM kullanici_bolgeler kb
      WHERE kb.kullanici_id = k.id AND kb.bolge_id = k.bolge_id
  );

-- 3) formen1: hem A hem B
DELETE FROM kullanici_bolgeler
WHERE kullanici_id = (SELECT id FROM kullanicilar WHERE kullanici_adi = 'formen1');

INSERT INTO kullanici_bolgeler (kullanici_id, bolge_id)
SELECT k.id, b.id
FROM kullanicilar k
CROSS JOIN bolgeler b
WHERE k.kullanici_adi = 'formen1'
  AND b.bolge_adi IN ('Yuksek Firin A Bolgesi', 'Yuksek Firin B Bolgesi');

UPDATE kullanicilar
SET bolge_id = (SELECT id FROM bolgeler WHERE bolge_adi = 'Yuksek Firin A Bolgesi'),
    gorev = 'Saha Formeni – Yüksek Fırın A/B'
WHERE kullanici_adi = 'formen1';
