package com.isg.ihlal.backend.dto;

import java.util.List;

/**
 * DTO-4 (tasarim_mimari.md): /api/auth/login basarili yanit.
 * bolgeId / bolgeIds yalnizca FORMEN rolu icin doludur.
 */
public record LoginResponseDTO(
        String token,
        Long kullaniciId,
        String kullaniciAdi,
        String rol,
        String adSoyad,
        Long bolgeId,
        List<Long> bolgeIds
) {
}
