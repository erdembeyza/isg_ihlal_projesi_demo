package com.isg.ihlal.backend.dto;

import java.util.List;

public record HaftalikRaporOzetDTO(
        String baslangic,
        String bitis,
        int toplamIhlal,
        int aktif,
        int cozuldu,
        int hataliTespit,
        List<BolgeOzet> bolgeOzetleri,
        List<TipOzet> tipOzetleri,
        List<SaatOzet> riskliSaatler
) {
    public record BolgeOzet(String bolgeAdi, int adet) {
    }

    public record TipOzet(String tipAdi, int adet) {
    }

    public record SaatOzet(int saat, int adet) {
    }
}
