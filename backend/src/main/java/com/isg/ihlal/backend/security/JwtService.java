package com.isg.ihlal.backend.security;

import com.isg.ihlal.backend.entity.Kullanici;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * MODUL-3 (tasarim_mimari.md): JWT uretimi ve dogrulamasi.
 * <p>
 * Uretilen token; kullanici id, rol ve bolge_id bilgilerini claim olarak
 * tasir, boylece sonraki her istekte veritabanina gitmeden rol/bolge bazli
 * yetkilendirme yapilabilir (bkz. JwtAuthenticationFilter).
 */
@Service
public class JwtService {

    private static final String CLAIM_KULLANICI_ID = "kullaniciId";
    private static final String CLAIM_ROL = "rol";
    private static final String CLAIM_BOLGE_ID = "bolgeId";

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
        Map<String, Object> claims = new HashMap<>();
        claims.put(CLAIM_KULLANICI_ID, kullanici.getId());
        claims.put(CLAIM_ROL, kullanici.getRol().name());
        if (kullanici.getBolge() != null) {
            claims.put(CLAIM_BOLGE_ID, kullanici.getBolge().getId());
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

    /**
     * Token imzasini ve suresini dogrular; gecersizse JwtException firlatir.
     * Cagiran taraf (JwtAuthenticationFilter) bu istisnayi yakalayip
     * kullaniciyi kimliksiz (anonymous) birakmakla sorumludur.
     */
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
        return new AuthenticatedUser(
                kullaniciIdNumber != null ? kullaniciIdNumber.longValue() : null,
                claims.getSubject(),
                claims.get(CLAIM_ROL, String.class),
                bolgeIdNumber != null ? bolgeIdNumber.longValue() : null
        );
    }
}
