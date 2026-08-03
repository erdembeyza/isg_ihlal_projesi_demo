package com.isg.ihlal.backend.dto;

/**
 * POST /api/kullanicilar basarili yaniti. sifreHash asla disariya verilmez.
 */
public record KullaniciResponseDTO(
        Long id,
        String kullaniciAdi,
        String adSoyad,
        String rol,
        Long bolgeId,
        Boolean aktifMi
) {
}
