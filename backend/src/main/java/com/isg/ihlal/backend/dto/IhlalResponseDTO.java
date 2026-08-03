package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

/**
 * DTO-2 (tasarim_mimari.md): Ihlal listesi/detayinda donen model.
 * fotoUrl, caginin rolune gore IhlalService tarafindan orijinal ya da
 * blurlu fotografin yoluna set edilir (formen -> blur, yonetici -> orijinal).
 */
public record IhlalResponseDTO(
        Long id,
        String bolgeAdi,
        String ihlalTipiAdi,
        LocalDateTime tespitZamani,
        String fotoUrl,
        String durum
) {
}
