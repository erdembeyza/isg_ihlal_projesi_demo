package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

public record PersonelYuzDTO(
        Long id,
        String fotoUrl,
        LocalDateTime olusturmaZamani
) {
}
