package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.BolgeDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.repository.BolgeRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * Tanimli tum uretim bolgelerini listeler (dropdown/filtre gibi kullanimlar icin).
 * Ozel bir rol kisiti yok: hem ISG_YONETICI hem FORMEN erisebilir, sadece
 * kimlik dogrulamasi (gecerli JWT) yeterlidir.
 */
@RestController
@RequestMapping("/api/bolgeler")
public class BolgeController {

    private final BolgeRepository bolgeRepository;

    public BolgeController(BolgeRepository bolgeRepository) {
        this.bolgeRepository = bolgeRepository;
    }

    @GetMapping
    public List<BolgeDTO> listele() {
        return bolgeRepository.findAll().stream()
                .map(this::toDto)
                .toList();
    }

    private BolgeDTO toDto(Bolge bolge) {
        return new BolgeDTO(bolge.getId(), bolge.getBolgeAdi(), bolge.getAciklama());
    }
}
