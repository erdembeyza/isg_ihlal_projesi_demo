package com.isg.ihlal.backend.dto;

import com.isg.ihlal.backend.entity.Rol;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * POST /api/kullanicilar istegi. Sadece ISG_YONETICI tarafindan cagrilir
 * (bkz. KullaniciController). bolgeId yalnizca rol=FORMEN icin anlamlidir;
 * ISG_YONETICI olusturulurken null birakilmalidir.
 */
public record KullaniciRequestDTO(

        @NotBlank(message = "kullaniciAdi zorunludur")
        @Size(max = 50)
        String kullaniciAdi,

        @NotBlank(message = "sifre zorunludur")
        @Size(min = 6, message = "sifre en az 6 karakter olmalidir")
        String sifre,

        @NotBlank(message = "adSoyad zorunludur")
        @Size(max = 100)
        String adSoyad,

        @NotNull(message = "rol zorunludur")
        Rol rol,

        Long bolgeId
) {
}
