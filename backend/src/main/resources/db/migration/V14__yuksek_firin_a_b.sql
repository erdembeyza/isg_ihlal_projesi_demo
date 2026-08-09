-- Yuksek Firin bolgesi (A/B kameralari ayni bolge_id altinda)
-- Formen tek bolgeye bagli oldugu icin A+B ihlal/kamera durumu ayni bolgede tutulur.
-- Beklenen id (V2/V3/V9 sonrasi): 4

INSERT INTO bolgeler (bolge_adi, aciklama)
SELECT 'Yuksek Firin', 'Yuksek firin — A ve B bolgesi kameralari (video ile canli simulasyon)'
WHERE NOT EXISTS (SELECT 1 FROM bolgeler WHERE bolge_adi = 'Yuksek Firin');

-- formen1: Yuksek Firin formenı (diger bolgeleri gormez)
UPDATE kullanicilar
SET bolge_id = (SELECT id FROM bolgeler WHERE bolge_adi = 'Yuksek Firin'),
    gorev = 'Saha Formeni – Yüksek Fırın'
WHERE kullanici_adi = 'formen1';
