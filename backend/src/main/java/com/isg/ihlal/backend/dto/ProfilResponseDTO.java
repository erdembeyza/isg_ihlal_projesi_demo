package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;
import java.util.List;

public record ProfilResponseDTO(
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
        String gorev,
        LocalDateTime sonGirisZamani
) {
}
