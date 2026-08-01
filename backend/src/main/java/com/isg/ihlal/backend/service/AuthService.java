package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.LoginRequestDTO;
import com.isg.ihlal.backend.dto.LoginResponseDTO;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.repository.KullaniciRepository;
import com.isg.ihlal.backend.security.JwtService;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * MODUL-3 (tasarim_mimari.md): /api/auth/login is mantigi.
 * Kullanici adi/sifre BCrypt ile dogrulanir, basariliysa JWT uretilir.
 */
@Service
public class AuthService {

    private final KullaniciRepository kullaniciRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(
            KullaniciRepository kullaniciRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService
    ) {
        this.kullaniciRepository = kullaniciRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public LoginResponseDTO login(LoginRequestDTO request) {
        Kullanici kullanici = kullaniciRepository.findByKullaniciAdi(request.kullaniciAdi())
                .orElseThrow(() -> new BadCredentialsException("Kullanici adi veya sifre hatali"));

        if (Boolean.FALSE.equals(kullanici.getAktifMi())) {
            throw new BadCredentialsException("Kullanici pasif durumda");
        }

        if (!passwordEncoder.matches(request.sifre(), kullanici.getSifreHash())) {
            throw new BadCredentialsException("Kullanici adi veya sifre hatali");
        }

        String token = jwtService.generateToken(kullanici);
        Long bolgeId = kullanici.getBolge() != null ? kullanici.getBolge().getId() : null;

        return new LoginResponseDTO(token, kullanici.getRol().name(), kullanici.getAdSoyad(), bolgeId);
    }
}
