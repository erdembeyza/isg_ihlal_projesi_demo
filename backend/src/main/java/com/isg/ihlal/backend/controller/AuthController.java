package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.LoginRequestDTO;
import com.isg.ihlal.backend.dto.LoginResponseDTO;
import com.isg.ihlal.backend.dto.ProfilGuncelleRequestDTO;
import com.isg.ihlal.backend.dto.ProfilResponseDTO;
import com.isg.ihlal.backend.dto.SifreDegistirRequestDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.service.AuthService;
import com.isg.ihlal.backend.service.KullaniciService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final KullaniciService kullaniciService;

    public AuthController(AuthService authService, KullaniciService kullaniciService) {
        this.authService = authService;
        this.kullaniciService = kullaniciService;
    }

    @PostMapping("/login")
    public ResponseEntity<LoginResponseDTO> login(@Valid @RequestBody LoginRequestDTO request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @GetMapping("/profil")
    public ProfilResponseDTO profil(@AuthenticationPrincipal AuthenticatedUser user) {
        return kullaniciService.profilGetir(user);
    }

    @PutMapping("/profil")
    public ProfilResponseDTO profilGuncelle(
            @AuthenticationPrincipal AuthenticatedUser user,
            @Valid @RequestBody ProfilGuncelleRequestDTO dto
    ) {
        return kullaniciService.profilGuncelle(user, dto);
    }

    @PutMapping("/sifre")
    public ResponseEntity<Void> sifreDegistir(
            @AuthenticationPrincipal AuthenticatedUser user,
            @Valid @RequestBody SifreDegistirRequestDTO dto
    ) {
        kullaniciService.sifreDegistir(user, dto);
        return ResponseEntity.noContent().build();
    }

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<Map<String, String>> handleBadCredentials(BadCredentialsException ex) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("hata", ex.getMessage()));
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<Map<String, String>> handleResponseStatus(ResponseStatusException ex) {
        return ResponseEntity
                .status(ex.getStatusCode())
                .body(Map.of("hata", ex.getReason() != null ? ex.getReason() : "Islem basarisiz"));
    }
}
