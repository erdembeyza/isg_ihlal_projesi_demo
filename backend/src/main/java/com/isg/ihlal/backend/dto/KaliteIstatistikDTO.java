package com.isg.ihlal.backend.dto;

import java.util.List;

public record KaliteIstatistikDTO(
        int toplamIhlal,
        int reddedilen,
        double falsePositiveOrani,
        int finetuneHavuzDosyaSayisi,
        List<HaftalikKaliteNoktasi> haftalikTrend
) {
    public record HaftalikKaliteNoktasi(
            String haftaEtiketi,
            int toplam,
            int reddedilen,
            double fpOrani
    ) {
    }
}
