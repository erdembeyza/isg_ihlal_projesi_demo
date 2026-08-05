package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.IslemLogDTO;
import com.isg.ihlal.backend.service.IslemLogService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/islem-loglari")
public class IslemLogController {

    private final IslemLogService islemLogService;

    public IslemLogController(IslemLogService islemLogService) {
        this.islemLogService = islemLogService;
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'GORUNTULEYICI')")
    public List<IslemLogDTO> listele(
            @RequestParam(defaultValue = "100") int limit,
            @RequestParam(required = false) String tip
    ) {
        return islemLogService.listele(limit, tip);
    }
}
