package com.isg.ihlal.backend.dto;

/**
 * DTO-5 (tasarim_mimari.md): GET /api/ihlaller/istatistik yanit modeli.
 * Bolge + ihlal tipi kirilimi bazinda son 7 gunluk toplam adet ve onceki
 * 7 gune gore yuzdesel degisim bilgisini tasir.
 */
public record IhlalIstatistikDTO(
        String bolgeAdi,
        String ihlalTipiAdi,
        Integer toplamAdet,
        Double yuzdeDegisim
) {
}
