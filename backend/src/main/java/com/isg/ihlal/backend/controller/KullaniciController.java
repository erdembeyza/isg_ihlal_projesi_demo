package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.KullaniciGuncelleRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciResponseDTO;
import com.isg.ihlal.backend.dto.SifreGuncelleRequestDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.service.KullaniciService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/kullanicilar")
public class KullaniciController {

    private final KullaniciService kullaniciService;

    public KullaniciController(KullaniciService kullaniciService) {
        this.kullaniciService = kullaniciService;
    }

    @GetMapping
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public List<KullaniciResponseDTO> listele() {
        return kullaniciService.listele();
    }

    @PostMapping
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<KullaniciResponseDTO> olustur(@Valid @RequestBody KullaniciRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(kullaniciService.olustur(dto));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public KullaniciResponseDTO guncelle(
            @PathVariable Long id,
            @Valid @RequestBody KullaniciGuncelleRequestDTO dto,
            @AuthenticationPrincipal AuthenticatedUser user
    ) {
        return kullaniciService.guncelle(id, dto, user);
    }

    @PutMapping("/{id}/sifre")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<Void> sifreGuncelle(
            @PathVariable Long id,
            @Valid @RequestBody SifreGuncelleRequestDTO dto,
            @AuthenticationPrincipal AuthenticatedUser user
    ) {
        kullaniciService.sifreGuncelle(id, dto, user);
        return ResponseEntity.noContent().build();
    }
}
