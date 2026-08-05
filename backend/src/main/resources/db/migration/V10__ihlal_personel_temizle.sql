-- ============================================================================
-- V10__ihlal_personel_temizle.sql
-- Ihlal kayitlarindaki personel/sicil eslesmesini kaldirir.
-- Kisi silueti ve ihlal tespiti devam eder; personel adi/sicil no gosterilmez.
-- ============================================================================

UPDATE ihlaller
SET personel_id = NULL
WHERE personel_id IS NOT NULL;
