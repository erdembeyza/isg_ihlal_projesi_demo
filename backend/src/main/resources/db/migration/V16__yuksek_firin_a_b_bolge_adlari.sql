-- A/B bolge adlarini panede dogru gostermek icin duzeltir.
-- cameras.yuksek-firin.json: a_bolgesi.mp4 -> bolge_id=4, b_bolgesi.mp4 -> bolge_id=5

-- id=4: a_bolgesi.mp4 (mevcut ihlaller burada)
UPDATE bolgeler
SET bolge_adi = 'Yüksek Fırın A Bolgesi',
    aciklama = 'Yüksek Fırın A bölgesi kamerası (a_bolgesi.mp4)'
WHERE id = 4;

-- id=5: b_bolgesi.mp4
UPDATE bolgeler
SET bolge_adi = 'Yüksek Fırın B Bolgesi',
    aciklama = 'Yüksek Fırın B bölgesi kamerası (b_bolgesi.mp4)'
WHERE id = 5;

-- V15'in yanlis ekledigi 3. kopyayi (ornegin id=6) B'ye tasir / siler
DO $$
DECLARE
    fazla_id BIGINT;
BEGIN
    SELECT id INTO fazla_id
    FROM bolgeler
    WHERE bolge_adi IN ('Yuksek Firin B Bolgesi', 'Yuksek Firin A Bolgesi', 'Yuksek Firin')
      AND id NOT IN (4, 5)
    ORDER BY id
    LIMIT 1;

    IF fazla_id IS NOT NULL THEN
        UPDATE ihlaller SET bolge_id = 5 WHERE bolge_id = fazla_id;
        UPDATE kamera_durumlari SET bolge_id = 5 WHERE bolge_id = fazla_id;

        INSERT INTO kullanici_bolgeler (kullanici_id, bolge_id)
        SELECT kb.kullanici_id, 5
        FROM kullanici_bolgeler kb
        WHERE kb.bolge_id = fazla_id
          AND NOT EXISTS (
              SELECT 1 FROM kullanici_bolgeler x
              WHERE x.kullanici_id = kb.kullanici_id AND x.bolge_id = 5
          );

        DELETE FROM kullanici_bolgeler WHERE bolge_id = fazla_id;
        UPDATE kullanicilar SET bolge_id = 4 WHERE bolge_id = fazla_id;
        DELETE FROM bolgeler WHERE id = fazla_id;
    END IF;
END $$;

-- Isimleri ASCII varyantlardan da temizle
UPDATE bolgeler
SET bolge_adi = 'Yüksek Fırın A Bolgesi'
WHERE bolge_adi IN ('Yuksek Firin A Bolgesi', 'Yuksek Firin', 'Yüksek Fırın')
  AND id = 4;

UPDATE bolgeler
SET bolge_adi = 'Yüksek Fırın B Bolgesi'
WHERE bolge_adi IN ('Yuksek Firin B Bolgesi')
  AND id = 5;

-- Yuksek Firin formenleri: A + B (eski formen1 veya formen_yf*)
DELETE FROM kullanici_bolgeler
WHERE kullanici_id IN (
    SELECT id FROM kullanicilar
    WHERE kullanici_adi IN ('formen1', 'formen_yf', 'formen_yf_deneme')
);

INSERT INTO kullanici_bolgeler (kullanici_id, bolge_id)
SELECT k.id, b.id
FROM kullanicilar k
CROSS JOIN bolgeler b
WHERE k.kullanici_adi IN ('formen1', 'formen_yf', 'formen_yf_deneme')
  AND b.id IN (4, 5);

UPDATE kullanicilar
SET bolge_id = 4,
    gorev = 'Saha Formeni – Yüksek Fırın A/B'
WHERE kullanici_adi IN ('formen1', 'formen_yf', 'formen_yf_deneme');
