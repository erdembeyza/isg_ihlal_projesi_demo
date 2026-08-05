package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.HaftalikRaporOzetDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.service.RaporService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/raporlar")
public class RaporController {

    private final RaporService raporService;

    public RaporController(RaporService raporService) {
        this.raporService = raporService;
    }

    @GetMapping("/haftalik")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public HaftalikRaporOzetDTO haftalikOzet(
            @AuthenticationPrincipal AuthenticatedUser user,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate baslangic,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate bitis
    ) {
        return raporService.ozet(user, baslangic, bitis);
    }

    @GetMapping("/haftalik.pdf")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public ResponseEntity<byte[]> haftalikPdf(
            @AuthenticationPrincipal AuthenticatedUser user,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate baslangic,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate bitis
    ) {
        byte[] pdf = raporService.pdfOlustur(user, baslangic, bitis);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"haftalik-ihlal-raporu.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }
}
