package com.isg.ihlal.backend.dto;

import java.util.List;

public record PersonelDTO(
        Long id,
        String sicilNo,
        String adSoyad,
        String departman,
        Long bolgeId,
        String bolgeAdi,
        Boolean aktifMi,
        int yuzSayisi,
        List<PersonelYuzDTO> yuzler
) {
}
