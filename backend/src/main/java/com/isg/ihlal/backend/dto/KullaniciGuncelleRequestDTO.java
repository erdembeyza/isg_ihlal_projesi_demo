package com.isg.ihlal.backend.dto;

import com.isg.ihlal.backend.entity.Rol;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record KullaniciGuncelleRequestDTO(

        @NotBlank(message = "kullaniciAdi zorunludur")
        @Size(min = 3, max = 50)
        String kullaniciAdi,

        @NotBlank(message = "adSoyad zorunludur")
        @Size(max = 100)
        String adSoyad,

        @NotNull(message = "rol zorunludur")
        Rol rol,

        Long bolgeId,

        @NotNull(message = "aktifMi zorunludur")
        Boolean aktifMi,

        /** Bos birakilirsa parola degismez. */
        String yeniSifre,

        @Size(max = 120)
        String eposta,

        @Size(max = 30)
        String telefon,

        @Size(max = 150)
        String gorev
) {
}
