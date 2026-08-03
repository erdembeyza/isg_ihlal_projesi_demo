-- ============================================================================
-- V4__ai_core_servis_hesabi.sql
-- Faz 7: Python AI Core servisinin POST /api/ihlaller ucuna istek atabilmesi
-- icin gecerli bir JWT alacagi ozel bir servis hesabi ekler.
--
-- NOT: /api/ihlaller POST ucunda ozel bir rol kisiti yoktur (bkz.
-- IhlalController#kaydet); herhangi bir kimlik dogrulanmis kullanici
-- cagirabilir. Bu hesaba yine de ISG_YONETICI rolu verilir (rol CHECK
-- kisiti yalnizca ISG_YONETICI/FORMEN degerlerini kabul eder); AI Core
-- yalnizca /api/ihlaller POST ucunu kullanir, panel/istatistik amacli
-- kullanilmaz.
--
-- sifre_hash alani BCrypt (cost=10) ile onceden hesaplanmistir.
-- kullanici_adi=ai_core_servis / sifre=AiCore123! (yalnizca dev/test ortami,
-- production'a alinmadan once mutlaka degistirilmelidir).
-- ============================================================================

INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, rol, bolge_id, aktif_mi) VALUES
    ('ai_core_servis', '$2b$10$8xDfg5RUmw6NvJK5z181pu2IEKKgABURSs2SDCkGvtqnUxgSm8ekW', 'AI Core Servis Hesabi', 'ISG_YONETICI', NULL, TRUE);
