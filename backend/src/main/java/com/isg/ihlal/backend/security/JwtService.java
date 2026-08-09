package com.isg.ihlal.backend.security;

import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.Kullanici;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * MODUL-3 (tasarim_mimari.md): JWT uretimi ve dogrulamasi.
 */
@Service
public class JwtService {

    private static final String CLAIM_KULLANICI_ID = "kullaniciId";
    private static final String CLAIM_ROL = "rol";
    private static final String CLAIM_BOLGE_ID = "bolgeId";
    private static final String CLAIM_BOLGE_IDS = "bolgeIds";

    private final SecretKey signingKey;
    private final long expirationMs;

    public JwtService(
            @Value("${jwt.secret}") String base64Secret,
            @Value("${jwt.expiration-ms}") long expirationMs
    ) {
        this.signingKey = Keys.hmacShaKeyFor(Base64.getDecoder().decode(base64Secret));
        this.expirationMs = expirationMs;
    }

    public String generateToken(Kullanici kullanici) {
        List<Long> bolgeIds = bolgeIdleriniTopla(kullanici);

        Map<String, Object> claims = new HashMap<>();
        claims.put(CLAIM_KULLANICI_ID, kullanici.getId());
        claims.put(CLAIM_ROL, kullanici.getRol().name());
        if (!bolgeIds.isEmpty()) {
            claims.put(CLAIM_BOLGE_ID, bolgeIds.getFirst());
            claims.put(CLAIM_BOLGE_IDS, bolgeIds);
        }

        Date now = new Date();
        Date expiry = new Date(now.getTime() + expirationMs);

        return Jwts.builder()
                .subject(kullanici.getKullaniciAdi())
                .claims(claims)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(signingKey)
                .compact();
    }

    public Claims parseClaims(String token) throws JwtException {
        return Jwts.parser()
                .verifyWith(signingKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public AuthenticatedUser toAuthenticatedUser(Claims claims) {
        Number kullaniciIdNumber = claims.get(CLAIM_KULLANICI_ID, Number.class);
        Number bolgeIdNumber = claims.get(CLAIM_BOLGE_ID, Number.class);
        List<Long> bolgeIds = bolgeIdsOku(claims.get(CLAIM_BOLGE_IDS));
        if (bolgeIds.isEmpty() && bolgeIdNumber != null) {
            bolgeIds = List.of(bolgeIdNumber.longValue());
        }
        return new AuthenticatedUser(
                kullaniciIdNumber != null ? kullaniciIdNumber.longValue() : null,
                claims.getSubject(),
                claims.get(CLAIM_ROL, String.class),
                bolgeIdNumber != null ? bolgeIdNumber.longValue() : null,
                bolgeIds
        );
    }

    private static List<Long> bolgeIdleriniTopla(Kullanici kullanici) {
        Set<Long> ids = new LinkedHashSet<>();
        if (kullanici.getBolgeler() != null) {
            for (Bolge bolge : kullanici.getBolgeler()) {
                if (bolge != null && bolge.getId() != null) {
                    ids.add(bolge.getId());
                }
            }
        }
        if (kullanici.getBolge() != null && kullanici.getBolge().getId() != null) {
            ids.add(kullanici.getBolge().getId());
        }
        return new ArrayList<>(ids);
    }

    private static List<Long> bolgeIdsOku(Object ham) {
        if (!(ham instanceof List<?> liste) || liste.isEmpty()) {
            return List.of();
        }
        List<Long> sonuc = new ArrayList<>();
        for (Object o : liste) {
            if (o instanceof Number n) {
                sonuc.add(n.longValue());
            }
        }
        return List.copyOf(sonuc);
    }
}
