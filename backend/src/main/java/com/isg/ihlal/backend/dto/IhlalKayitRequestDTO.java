package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

/**
 * DTO-1 (tasarim_mimari.md): AI Core servisinin POST /api/ihlaller ucuna
 * gonderdigi yeni ihlal kaydi istegi. Fotograflar base64 string olarak
 * tasinir; backend bunlari cozup dosya sistemine yazar (bkz. FileStorageService).
 */
public record IhlalKayitRequestDTO(

        @NotNull(message = "bolgeId zorunludur")
        Long bolgeId,

        @NotNull(message = "ihlalTipiId zorunludur")
        Short ihlalTipiId,

        @NotNull(message = "tespitZamani zorunludur")
        LocalDateTime tespitZamani,

        @NotBlank(message = "orijinalFotoBase64 zorunludur")
        String orijinalFotoBase64,

        @NotBlank(message = "blurluFotoBase64 zorunludur")
        String blurluFotoBase64
) {
}
