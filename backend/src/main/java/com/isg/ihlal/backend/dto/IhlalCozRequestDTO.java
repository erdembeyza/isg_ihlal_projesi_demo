package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.Size;

public record IhlalCozRequestDTO(
        @Size(max = 500, message = "coz notu en fazla 500 karakter olabilir")
        String not
) {
}
