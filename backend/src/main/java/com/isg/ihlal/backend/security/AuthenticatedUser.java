package com.isg.ihlal.backend.security;

/**
 * JWT icindeki claim'lerden (kullaniciId, rol, bolgeId) kurulan, dogrulanmis
 * istek boyunca SecurityContext'te tasinan "kimlik" nesnesi.
 * <p>
 * Not: Bu nesne her istekte veritabani sorgusu yapilmadan, dogrudan token
 * icindeki bilgilerden olusturulur (stateless authentication).
 */
public record AuthenticatedUser(
        Long kullaniciId,
        String kullaniciAdi,
        String rol,
        Long bolgeId
) {
}
