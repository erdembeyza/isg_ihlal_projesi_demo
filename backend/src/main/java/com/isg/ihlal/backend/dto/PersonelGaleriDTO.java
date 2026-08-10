package com.isg.ihlal.backend.dto;

import java.util.List;

public record PersonelGaleriDTO(
        Long personelId,
        String sicilNo,
        String adSoyad,
        List<PersonelGaleriYuzDTO> yuzler
) {
}
