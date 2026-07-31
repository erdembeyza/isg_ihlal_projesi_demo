-- ============================================================================
-- V2__seed.sql
-- Baslangic (seed) verileri: ihlal tipleri, ornek bolge, admin + formen
-- kullanicilari.
--
-- NOT: sifre_hash alanlari BCrypt (cost=10) ile onceden hesaplanmistir.
-- Duz metin sifreler bu dosyada YER ALMAZ; sadece gelistirme/test ortami
-- icin gecerlidir, production'a alinmadan once mutlaka degistirilmelidir.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Ornek bolge
-- ----------------------------------------------------------------------------
INSERT INTO bolgeler (bolge_adi, aciklama) VALUES
    ('Yuksek Firin-1', 'Ana uretim hatti - yuksek firin bolgesi (test/demo bolgesi)');

-- ----------------------------------------------------------------------------
-- Ihlal tipleri (KDD - Kisisel Koruyucu Donanim)
-- ----------------------------------------------------------------------------
INSERT INTO ihlal_tipleri (tip_adi, aciklama) VALUES
    ('BARET', 'Baret (kafa koruyucu) takilmamasi ihlali'),
    ('YELEK', 'Reflektorlu is yelegi giyilmemesi ihlali'),
    ('GOZLUK', 'Koruyucu gozluk takilmamasi ihlali');

-- ----------------------------------------------------------------------------
-- Kullanicilar: 1 ISG yoneticisi (tum fabrika) + 1 formen (tek bolge)
-- kullanici_adi=admin   / sifre=Admin123!   (yalnizca dev/test ortami)
-- kullanici_adi=formen1 / sifre=Formen123!  (yalnizca dev/test ortami)
-- ----------------------------------------------------------------------------
INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, rol, bolge_id, aktif_mi) VALUES
    ('admin', '$2b$10$T0.1EmoI1yFZUEGGJOAVl.gQqFMZ.H5oqdcLJiT3hnP/pbzrIdJES', 'Beyza Erdem', 'ISG_YONETICI', NULL, TRUE),
    ('formen1', '$2b$10$hXZihvD5iJNgQi0H9LD2Z.cZeG1EWiTjFn09yLWkIRgHIA35eVwiS', 'Formen Bir', 'FORMEN',
        (SELECT id FROM bolgeler WHERE bolge_adi = 'Yuksek Firin-1'), TRUE);
