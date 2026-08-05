package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public record KameraHeartbeatDTO(
        @NotNull Long bolgeId,
        @NotBlank String kameraAdi,
        LocalDateTime sonKareZamani,
        Double fps
) {
}
