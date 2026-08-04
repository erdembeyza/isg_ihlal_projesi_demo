-- Demo kameralarinin panelde anlamli bolge adlariyla gorunmesi.
-- bolge_id=1: bilgisayar webkami (Veri Merkezi)
-- bolge_id=2: telefon kamerasi (1. Sicak Haddehane)
UPDATE bolgeler
SET bolge_adi = 'Veri Merkezi',
    aciklama = 'Veri merkezi guvenlik kamerasi (demo: bilgisayar webkami)'
WHERE id = 1;

UPDATE bolgeler
SET bolge_adi = '1. Sicak Haddehane',
    aciklama = '1. sicak haddehane kamerasi (demo: telefon kamerasi)'
WHERE id = 2;
