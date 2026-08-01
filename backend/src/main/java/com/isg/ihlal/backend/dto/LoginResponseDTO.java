package com.isg.ihlal.backend.dto;

/**
 * DTO-4 (tasarim_mimari.md): /api/auth/login basarili yanit.
 * bolgeId yalnizca FORMEN rolu icin doludur; ISG_YONETICI icin null doner
 * (tum fabrikaya erisimi oldugu icin belirli bir bolgeye baglanmaz).
 */
public record LoginResponseDTO(
        String token,
        String rol,
        String adSoyad,
        Long bolgeId
) {
}
