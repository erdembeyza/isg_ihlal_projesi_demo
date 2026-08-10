package com.isg.ihlal.backend.dto;

/**
 * AI Core galeri senkronu: yuz fotografi base64 olarak tasinir.
 */
public record PersonelGaleriYuzDTO(
        Long yuzId,
        String fotoBase64
) {
}
