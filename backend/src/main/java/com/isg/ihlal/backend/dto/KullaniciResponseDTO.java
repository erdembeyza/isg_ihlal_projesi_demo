package com.isg.ihlal.backend.dto;

import java.util.List;

public record KullaniciResponseDTO(
        Long id,
        String kullaniciAdi,
        String adSoyad,
        String rol,
        Long bolgeId,
        String bolgeAdi,
        List<Long> bolgeIds,
        Boolean aktifMi,
        String eposta,
        String telefon,
        String gorev
) {
}
