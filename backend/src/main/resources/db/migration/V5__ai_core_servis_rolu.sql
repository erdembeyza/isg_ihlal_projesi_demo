-- ============================================================================
-- V5__ai_core_servis_rolu.sql
-- AI Core servis hesabini panel rollerinden ayirir.
-- POST /api/ihlaller yalnizca AI_CORE_SERVIS rolu ile cagrilabilir;
-- ISG_YONETICI / FORMEN hesaplari bu ucu kullanamaz.
-- ============================================================================

ALTER TABLE kullanicilar DROP CONSTRAINT ck_kullanici_rol;

ALTER TABLE kullanicilar ADD CONSTRAINT ck_kullanici_rol
    CHECK (rol IN ('ISG_YONETICI', 'FORMEN', 'AI_CORE_SERVIS'));

UPDATE kullanicilar
SET rol = 'AI_CORE_SERVIS'
WHERE kullanici_adi = 'ai_core_servis';
