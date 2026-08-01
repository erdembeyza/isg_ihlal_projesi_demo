package com.isg.ihlal.backend.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * DTO-3 (tasarim_mimari.md): /api/auth/login istegi.
 * Kullanicinin sisteme giris icin gonderdigi kimlik bilgileri.
 */
public record LoginRequestDTO(

        @NotBlank(message = "kullaniciAdi bos olamaz")
        String kullaniciAdi,

        @NotBlank(message = "sifre bos olamaz")
        String sifre
) {
}
