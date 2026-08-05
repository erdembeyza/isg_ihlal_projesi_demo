package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.KameraDurumDTO;
import com.isg.ihlal.backend.dto.KameraHeartbeatDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.KameraDurumu;
import com.isg.ihlal.backend.entity.Rol;
import com.isg.ihlal.backend.repository.BolgeRepository;
import com.isg.ihlal.backend.repository.KameraDurumuRepository;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class KameraDurumService {

    private final KameraDurumuRepository kameraDurumuRepository;
    private final BolgeRepository bolgeRepository;
    private final long offlineSaniye;

    public KameraDurumService(
            KameraDurumuRepository kameraDurumuRepository,
            BolgeRepository bolgeRepository,
            @Value("${app.kamera-offline-saniye:30}") long offlineSaniye
    ) {
        this.kameraDurumuRepository = kameraDurumuRepository;
        this.bolgeRepository = bolgeRepository;
        this.offlineSaniye = offlineSaniye;
    }

    @Transactional
    public KameraDurumDTO heartbeat(KameraHeartbeatDTO dto) {
        Bolge bolge = bolgeRepository.findById(dto.bolgeId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Bolge bulunamadi: " + dto.bolgeId()));

        String kameraAdi = dto.kameraAdi().trim();
        KameraDurumu durum = kameraDurumuRepository
                .findByBolgeIdAndKameraAdi(bolge.getId(), kameraAdi)
                .orElseGet(KameraDurumu::new);

        durum.setBolge(bolge);
        durum.setKameraAdi(kameraAdi);
        durum.setOnlineMi(Boolean.TRUE);
        durum.setSonKareZamani(dto.sonKareZamani() != null ? dto.sonKareZamani() : LocalDateTime.now());
        durum.setFps(dto.fps());
        durum.setGuncellemeZamani(LocalDateTime.now());

        return toDto(kameraDurumuRepository.save(durum), LocalDateTime.now());
    }

    public List<KameraDurumDTO> listele(AuthenticatedUser user) {
        LocalDateTime simdi = LocalDateTime.now();
        List<KameraDurumu> kayitlar = isFormen(user)
                ? kameraDurumuRepository.findByBolgeId(user.bolgeId())
                : kameraDurumuRepository.findAllByOrderByBolgeIdAscKameraAdiAsc();

        return kayitlar.stream()
                .map(k -> toDto(k, simdi))
                .toList();
    }

    private KameraDurumDTO toDto(KameraDurumu k, LocalDateTime simdi) {
        boolean online = Boolean.TRUE.equals(k.getOnlineMi())
                && k.getGuncellemeZamani() != null
                && !k.getGuncellemeZamani().isBefore(simdi.minusSeconds(offlineSaniye));

        return new KameraDurumDTO(
                k.getId(),
                k.getBolge().getId(),
                k.getBolge().getBolgeAdi(),
                k.getKameraAdi(),
                online,
                k.getSonKareZamani(),
                k.getFps(),
                k.getGuncellemeZamani()
        );
    }

    private boolean isFormen(AuthenticatedUser user) {
        return Rol.FORMEN.name().equals(user.rol());
    }
}
