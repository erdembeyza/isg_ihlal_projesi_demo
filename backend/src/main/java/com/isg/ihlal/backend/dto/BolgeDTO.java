package com.isg.ihlal.backend.dto;

/**
 * GET /api/bolgeler yanitinda kullanilan basit bolge modeli.
 */
public record BolgeDTO(
        Long id,
        String bolgeAdi,
        String aciklama
) {
}
