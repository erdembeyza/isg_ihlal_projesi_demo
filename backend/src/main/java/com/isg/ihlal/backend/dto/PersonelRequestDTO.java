package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record PersonelRequestDTO(
        @NotBlank(message = "sicilNo zorunludur")
        @Size(max = 50)
        String sicilNo,

        @NotBlank(message = "adSoyad zorunludur")
        @Size(max = 100)
        String adSoyad,

        @Size(max = 100)
        String departman,

        Long bolgeId,

        Boolean aktifMi
) {
}
