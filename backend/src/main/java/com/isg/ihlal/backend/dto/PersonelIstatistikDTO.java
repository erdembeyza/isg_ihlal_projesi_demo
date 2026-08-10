package com.isg.ihlal.backend.dto;

import java.util.List;

/**
 * Personel bazli ihlal ozeti: en cok ihlal yapan personeller listesi icin.
 */
public record PersonelIstatistikDTO(
        Long personelId,
        String personelAdi,
        String sicilNo,
        String departman,
        int toplamIhlal,
        String enCokIhlalKategorisi,
        List<TipAdet> tipDagilimi
) {
    public record TipAdet(String tipAdi, int adet) {
    }
}
