package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ProfilGuncelleRequestDTO(

        @NotBlank(message = "adSoyad zorunludur")
        @Size(max = 100)
        String adSoyad
) {
}
