package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.FinetuneHavuzSenkronDTO;
import com.isg.ihlal.backend.dto.IhlalIstatistikDTO;
import com.isg.ihlal.backend.dto.IhlalKayitRequestDTO;
import com.isg.ihlal.backend.dto.IhlalRedRequestDTO;
import com.isg.ihlal.backend.dto.IhlalResponseDTO;
import com.isg.ihlal.backend.dto.PersonelIstatistikDTO;
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
     * Yalnizca AI_CORE_SERVIS rolu (V5) ile cagrilabilir.
     */
    @PostMapping
    @PreAuthorize("hasRole('AI_CORE_SERVIS')")
    public ResponseEntity<IhlalResponseDTO> kaydet(@Valid @RequestBody IhlalKayitRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(ihlalService.kaydet(dto));
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN')")
    public List<IhlalResponseDTO> listele(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.listele(user);
    }

    @GetMapping("/istatistik")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN')")
    public List<IhlalIstatistikDTO> istatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.istatistik(user);
    }

    @GetMapping("/istatistik/personel")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN')")
    public List<PersonelIstatistikDTO> personelIstatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.personelIstatistik(user);
    }

    /**
     * MODUL-6: mevcut HATALI_TESPIT orijinal fotolarini fine-tune havuzuna senkronize eder.
     * Path'te literal segment, /{id} ile catismasin diye id mapping'inden once tanimlanir.
     */
    @PostMapping("/finetune-havuz/senkronize")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public FinetuneHavuzSenkronDTO finetuneHavuzunuSenkronizeEt() {
        return ihlalService.finetuneHavuzunuSenkronizeEt();
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN')")
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

    @PostMapping("/{id}/coz")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN')")
    public IhlalResponseDTO coz(
            @PathVariable Long id,
            @AuthenticationPrincipal AuthenticatedUser user
    ) {
        return ihlalService.coz(id, user);
    }
}
