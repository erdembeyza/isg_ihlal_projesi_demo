package com.isg.ihlal.backend.security;

import java.util.List;

/**
 * JWT icindeki claim'lerden kurulan, dogrulanmis istek boyunca
 * SecurityContext'te tasinan kimlik nesnesi.
 * <p>
 * FORMEN icin {@code bolgeIds} birden fazla bolgeyi kapsayabilir
 * (or. Yuksek Firin A + B). {@code bolgeId} birincil/geriye donuk alandir.
 */
public record AuthenticatedUser(
        Long kullaniciId,
        String kullaniciAdi,
        String rol,
        Long bolgeId,
        List<Long> bolgeIds
) {
    public AuthenticatedUser {
        bolgeIds = bolgeIds == null ? List.of() : List.copyOf(bolgeIds);
    }

    public List<Long> erisilebilirBolgeIds() {
        if (!bolgeIds.isEmpty()) {
            return bolgeIds;
        }
        return bolgeId != null ? List.of(bolgeId) : List.of();
    }

    public boolean bolgeyeErisebilir(Long hedefBolgeId) {
        return hedefBolgeId != null && erisilebilirBolgeIds().contains(hedefBolgeId);
    }
}
