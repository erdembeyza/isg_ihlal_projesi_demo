package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.KullaniciRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciResponseDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.entity.Rol;
import com.isg.ihlal.backend.repository.BolgeRepository;
import com.isg.ihlal.backend.repository.KullaniciRepository;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * POST /api/kullanicilar is mantigi. Yalnizca ISG_YONETICI rolu tarafindan
 * cagrilabilir (yetki kontrolu KullaniciController'da @PreAuthorize ile yapilir).
 */
@Service
public class KullaniciService {

    private final KullaniciRepository kullaniciRepository;
    private final BolgeRepository bolgeRepository;
    private final PasswordEncoder passwordEncoder;

    public KullaniciService(
            KullaniciRepository kullaniciRepository,
            BolgeRepository bolgeRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.kullaniciRepository = kullaniciRepository;
        this.bolgeRepository = bolgeRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public KullaniciResponseDTO olustur(KullaniciRequestDTO dto) {
        if (dto.rol() == Rol.AI_CORE_SERVIS) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "AI_CORE_SERVIS rolu panel uzerinden olusturulamaz"
            );
        }

        if (kullaniciRepository.existsByKullaniciAdi(dto.kullaniciAdi())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Bu kullanici adi zaten kullanimda: " + dto.kullaniciAdi());
        }

        Bolge bolge = null;
        if (dto.rol() == Rol.FORMEN) {
            if (dto.bolgeId() == null) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "FORMEN rolu icin bolgeId zorunludur");
            }
            bolge = bolgeRepository.findById(dto.bolgeId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Bolge bulunamadi: " + dto.bolgeId()));
        }

        Kullanici kullanici = new Kullanici();
        kullanici.setKullaniciAdi(dto.kullaniciAdi());
        kullanici.setSifreHash(passwordEncoder.encode(dto.sifre()));
        kullanici.setAdSoyad(dto.adSoyad());
        kullanici.setRol(dto.rol());
        kullanici.setBolge(bolge);
        kullanici.setAktifMi(Boolean.TRUE);

        Kullanici kaydedilen = kullaniciRepository.save(kullanici);

        return new KullaniciResponseDTO(
                kaydedilen.getId(),
                kaydedilen.getKullaniciAdi(),
                kaydedilen.getAdSoyad(),
                kaydedilen.getRol().name(),
                kaydedilen.getBolge() != null ? kaydedilen.getBolge().getId() : null,
                kaydedilen.getAktifMi()
        );
    }
}
