package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.KameraDurumDTO;
import com.isg.ihlal.backend.dto.KameraHeartbeatDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.service.KameraDurumService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/kameralar")
public class KameraController {

    private final KameraDurumService kameraDurumService;

    public KameraController(KameraDurumService kameraDurumService) {
        this.kameraDurumService = kameraDurumService;
    }

    @PostMapping("/heartbeat")
    @PreAuthorize("hasRole('AI_CORE_SERVIS')")
    public ResponseEntity<KameraDurumDTO> heartbeat(@Valid @RequestBody KameraHeartbeatDTO dto) {
        return ResponseEntity.status(HttpStatus.OK).body(kameraDurumService.heartbeat(dto));
    }

    @GetMapping("/durum")
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public List<KameraDurumDTO> durum(@AuthenticationPrincipal AuthenticatedUser user) {
        return kameraDurumService.listele(user);
    }
}
