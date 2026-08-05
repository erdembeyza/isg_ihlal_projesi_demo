package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

public record IslemLogDTO(
        Long id,
        Long kullaniciId,
        String kullaniciAdi,
        String adSoyad,
        String islemTipi,
        Long ilgiliIhlalId,
        LocalDateTime islemZamani,
        String detay
) {
}
