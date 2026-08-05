package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

/**
 * DTO-2 (tasarim_mimari.md): Ihlal listesi/detayinda donen model.
 * fotoUrl, kanit fotografının erisim yoludur.
 */
public record IhlalResponseDTO(
        Long id,
        String bolgeAdi,
        String ihlalTipiAdi,
        LocalDateTime tespitZamani,
        String fotoUrl,
        String durum,
        Long personelId,
        String personelAdi,
        String personelSicilNo,
        String cozNotu,
        Integer sureSaniye
) {
}
