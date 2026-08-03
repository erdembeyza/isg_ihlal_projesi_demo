package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.KullaniciRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciResponseDTO;
import com.isg.ihlal.backend.service.KullaniciService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Yeni formen/kullanici tanimlama ucu. Yalnizca ISG_YONETICI yetkilidir;
 * yetkisiz denemeler @PreAuthorize sayesinde SecurityConfig'deki
 * accessDeniedHandler uzerinden 403 doner.
 */
@RestController
@RequestMapping("/api/kullanicilar")
public class KullaniciController {

    private final KullaniciService kullaniciService;

    public KullaniciController(KullaniciService kullaniciService) {
        this.kullaniciService = kullaniciService;
    }

    @PostMapping
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<KullaniciResponseDTO> olustur(@Valid @RequestBody KullaniciRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(kullaniciService.olustur(dto));
    }
}
