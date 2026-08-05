package com.isg.ihlal.backend.dto;

public record KullaniciResponseDTO(
        Long id,
        String kullaniciAdi,
        String adSoyad,
        String rol,
        Long bolgeId,
        String bolgeAdi,
        Boolean aktifMi,
        String eposta,
        String telefon,
        String gorev
) {
}
