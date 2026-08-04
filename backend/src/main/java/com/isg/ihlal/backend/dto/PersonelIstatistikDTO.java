package com.isg.ihlal.backend.dto;

/**
 * Personel bazli ihlal ozeti: en cok ihlal yapan personeller listesi icin.
 */
public record PersonelIstatistikDTO(
        Long personelId,
        String personelAdi,
        String sicilNo,
        String departman,
        int toplamIhlal,
        String enCokIhlalKategorisi
) {
}
