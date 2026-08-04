-- 1. Soguk Haddehane bolgesi (tablet / 3. kamera)
INSERT INTO bolgeler (bolge_adi, aciklama)
SELECT '1. Soguk Haddehane', '1. soguk haddehane kamerasi (demo: tablet kamerasi)'
WHERE NOT EXISTS (
    SELECT 1 FROM bolgeler WHERE bolge_adi = '1. Soguk Haddehane'
);
