-- ============================================================================
-- V12__kullanici_profil_demo.sql
-- Profil demo alanlari + ornek formenler + seed iletisim bilgileri
-- ============================================================================

ALTER TABLE kullanicilar
    ADD COLUMN eposta VARCHAR(120);

ALTER TABLE kullanicilar
    ADD COLUMN telefon VARCHAR(30);

ALTER TABLE kullanicilar
    ADD COLUMN gorev VARCHAR(150);

UPDATE kullanicilar
SET ad_soyad = 'Beyza Erdem',
    eposta = 'beyza.erdem@erdemir.com',
    telefon = '+90 555 100 00 01',
    gorev = 'ISG Koordinatörü – Tüm Fabrika'
WHERE kullanici_adi = 'admin';

UPDATE kullanicilar
SET ad_soyad = 'Mehmet Kaya',
    eposta = 'mehmet.kaya@erdemir.com',
    telefon = '+90 555 200 00 01',
    gorev = 'Saha Formeni – Yüksek Fırın-1'
WHERE kullanici_adi = 'formen1';

UPDATE kullanicilar
SET ad_soyad = 'Ayşe Yılmaz',
    eposta = 'ayse.yilmaz@erdemir.com',
    telefon = '+90 555 300 00 01',
    gorev = 'Üst Yönetim İzleyici – Raporlama'
WHERE kullanici_adi = 'izleyici';

-- formen2 / Formen123! (dev/test)
INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, rol, bolge_id, aktif_mi, eposta, telefon, gorev)
SELECT
    'formen2',
    '$2b$10$hXZihvD5iJNgQi0H9LD2Z.cZeG1EWiTjFn09yLWkIRgHIA35eVwiS',
    'Ayşe Demir',
    'FORMEN',
    b.id,
    TRUE,
    'ayse.demir@erdemir.com',
    '+90 555 200 00 02',
    'Saha Formeni – Sıcak Haddehane-2'
FROM bolgeler b
WHERE b.bolge_adi = 'Sicak Haddehane-2'
  AND NOT EXISTS (SELECT 1 FROM kullanicilar k WHERE k.kullanici_adi = 'formen2');

-- formen3 / Formen123! (dev/test)
INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, rol, bolge_id, aktif_mi, eposta, telefon, gorev)
SELECT
    'formen3',
    '$2b$10$hXZihvD5iJNgQi0H9LD2Z.cZeG1EWiTjFn09yLWkIRgHIA35eVwiS',
    'Can Öztürk',
    'FORMEN',
    b.id,
    TRUE,
    'can.ozturk@erdemir.com',
    '+90 555 200 00 03',
    'Saha Formeni – 1. Soğuk Haddehane'
FROM bolgeler b
WHERE b.bolge_adi = '1. Soguk Haddehane'
  AND NOT EXISTS (SELECT 1 FROM kullanicilar k WHERE k.kullanici_adi = 'formen3');
