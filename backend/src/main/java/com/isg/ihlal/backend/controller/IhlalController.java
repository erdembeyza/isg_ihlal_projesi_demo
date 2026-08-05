package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.FinetuneHavuzSenkronDTO;
import com.isg.ihlal.backend.dto.IhlalCozRequestDTO;
import com.isg.ihlal.backend.dto.IhlalIstatistikDTO;
import com.isg.ihlal.backend.dto.IhlalKayitRequestDTO;
import com.isg.ihlal.backend.dto.IhlalRedRequestDTO;
import com.isg.ihlal.backend.dto.IhlalResponseDTO;
import com.isg.ihlal.backend.dto.KaliteIstatistikDTO;
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

@RestController
@RequestMapping("/api/ihlaller")
public class IhlalController {

    private final IhlalService ihlalService;

    public IhlalController(IhlalService ihlalService) {
        this.ihlalService = ihlalService;
    }

    @PostMapping
    @PreAuthorize("hasRole('AI_CORE_SERVIS')")
    public ResponseEntity<IhlalResponseDTO> kaydet(@Valid @RequestBody IhlalKayitRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(ihlalService.kaydet(dto));
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public List<IhlalResponseDTO> listele(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.listele(user);
    }

    @GetMapping("/istatistik")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public List<IhlalIstatistikDTO> istatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.istatistik(user);
    }

    @GetMapping("/istatistik/personel")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public List<PersonelIstatistikDTO> personelIstatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.personelIstatistik(user);
    }

    @GetMapping("/istatistik/kalite")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'GORUNTULEYICI')")
    public KaliteIstatistikDTO kaliteIstatistik(@AuthenticationPrincipal AuthenticatedUser user) {
        return ihlalService.kaliteIstatistik(user);
    }

    @PostMapping("/finetune-havuz/senkronize")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public FinetuneHavuzSenkronDTO finetuneHavuzunuSenkronizeEt() {
        return ihlalService.finetuneHavuzunuSenkronizeEt();
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
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
            @RequestBody(required = false) @Valid IhlalCozRequestDTO dto,
            @AuthenticationPrincipal AuthenticatedUser user
    ) {
        return ihlalService.coz(id, dto, user);
    }
}
