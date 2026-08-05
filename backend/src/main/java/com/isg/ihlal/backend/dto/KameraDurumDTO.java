package com.isg.ihlal.backend.dto;

import java.time.LocalDateTime;

public record KameraDurumDTO(
        Long id,
        Long bolgeId,
        String bolgeAdi,
        String kameraAdi,
        boolean onlineMi,
        LocalDateTime sonKareZamani,
        Double fps,
        LocalDateTime guncellemeZamani
) {
}
