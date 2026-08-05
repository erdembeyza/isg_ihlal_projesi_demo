package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record SifreDegistirRequestDTO(

        @NotBlank(message = "mevcutSifre zorunludur")
        String mevcutSifre,

        @NotBlank(message = "yeniSifre zorunludur")
        @Size(min = 6, message = "yeniSifre en az 6 karakter olmalidir")
        String yeniSifre
) {
}
