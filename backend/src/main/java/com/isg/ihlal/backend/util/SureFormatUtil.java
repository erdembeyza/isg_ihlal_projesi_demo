package com.isg.ihlal.backend.util;

import java.util.ArrayList;
import java.util.List;

public final class SureFormatUtil {

    private SureFormatUtil() {
    }

    public static String metin(Integer toplamSaniye) {
        if (toplamSaniye == null) {
            return "-";
        }
        return metin(toplamSaniye.longValue());
    }

    public static String metin(long toplamSaniye) {
        long s = Math.max(0, toplamSaniye);

        if (s < 60) {
            return s + " sn";
        }

        long gun = s / 86_400;
        long sa = (s % 86_400) / 3_600;
        long dk = (s % 3_600) / 60;

        List<String> parcalar = new ArrayList<>();
        if (gun > 0) {
            parcalar.add(gun + " gün");
        }
        if (sa > 0) {
            parcalar.add(sa + " sa");
        }
        if (dk > 0) {
            parcalar.add(dk + " dk");
        }

        return parcalar.isEmpty() ? s + " sn" : String.join(" ", parcalar);
    }
}
