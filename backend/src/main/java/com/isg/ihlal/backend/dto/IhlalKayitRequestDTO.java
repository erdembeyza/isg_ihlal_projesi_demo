package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

/**
 * DTO-1 (tasarim_mimari.md): AI Core servisinin POST /api/ihlaller ucuna
 * gonderdigi yeni ihlal kaydi istegi. Fotograf base64 string olarak
 * tasinir; backend bunu cozup dosya sistemine yazar (bkz. FileStorageService).
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

        /** Opsiyonel: AI / manuel personel eslestirmesi (personel.id). */
        Long personelId,

        /** Opsiyonel: personelId yoksa sicil no ile eslestirme. */
        String personelSicilNo,

        /** Opsiyonel: AI Core track boyunca biriken ihlal suresi (saniye). */
        Integer sureSaniye
) {
}
