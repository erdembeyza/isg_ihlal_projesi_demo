-- Basarisiz giris denemeleri: bilinmeyen kullanici adlari icin kullanici_id opsiyonel
ALTER TABLE islem_loglari
    ALTER COLUMN kullanici_id DROP NOT NULL;

ALTER TABLE islem_loglari
    ADD COLUMN denenen_kullanici_adi VARCHAR(50);

CREATE INDEX idx_islem_loglari_islem_tipi ON islem_loglari (islem_tipi);
