package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.IhlalIstatistikDTO;
import com.isg.ihlal.backend.dto.IhlalKayitRequestDTO;
import com.isg.ihlal.backend.dto.IhlalRedRequestDTO;
import com.isg.ihlal.backend.dto.IhlalResponseDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.service.IhlalService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * MODUL-2 (tasarim_mimari.md): ihlal servisleri.
 * Rol bazli kapsam (formen: kendi bolgesi, yonetici: tum fabrika) IhlalService
 * icinde, gecerli JWT'den cozulen AuthenticatedUser uzerinden uygulanir.
 */
@RestController
@RequestMapping("/api/ihlaller")
public class IhlalController {

    private final IhlalService ihlalService;

    public IhlalController(IhlalService ihlalService) {
        this.ihlalService = ihlalService;
    }

    /**
     * AI Core servisinin yeni tespit ettigi ihlali islemek icin kullandigi uc.
     * Ozel bir rol kisiti yoktur; gecerli bir JWT ile herhangi bir kimlik
     * dogrulanmis istemci (ör. AI Core icin ayrilacak servis hesabi) cagirabilir.
     */
    @PostMapping
    public ResponseEntity<IhlalResponseDTO> kaydet(@Valid @RequestBody IhlalKayitRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(ihlalService.kaydet(dto));
    }

    @GetMapping
    public List<IhlalResponseDTO> listele(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.listele(user);
    }

    @GetMapping("/istatistik")
    public List<IhlalIstatistikDTO> istatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.istatistik(user);
    }

    @GetMapping("/{id}")
    public IhlalResponseDTO detay(@PathVariable Long id, @AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.detay(id, user);
    }

    @PostMapping("/{id}/reddet")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public IhlalResponseDTO reddet(
            @PathVariable Long id,
            @RequestBody(required = false) IhlalRedRequestDTO dto,
            @AuthenticationPrincipal AuthenticatedUser user
    ) {
        return ihlalService.reddet(id, dto, user);
    }
}
