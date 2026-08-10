package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;

public record YuzYukleRequestDTO(
        @NotBlank(message = "fotoBase64 zorunludur")
        String fotoBase64
) {
}
