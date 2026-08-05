package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

public record ProfilResponseDTO(
        Long id,
        String kullaniciAdi,
        String adSoyad,
        String rol,
        Long bolgeId,
        String bolgeAdi,
        Boolean aktifMi,
        String eposta,
        String telefon,
        String gorev,
        LocalDateTime sonGirisZamani
) {
}
