package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.IslemLogDTO;
import com.isg.ihlal.backend.entity.IslemLog;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.repository.IslemLogRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class IslemLogService {

    private final IslemLogRepository islemLogRepository;

    public IslemLogService(IslemLogRepository islemLogRepository) {
        this.islemLogRepository = islemLogRepository;
    }

    public List<IslemLogDTO> listele(int limit, String tip) {
        int guvenliLimit = Math.min(Math.max(limit, 1), 500);
        PageRequest page = PageRequest.of(0, guvenliLimit);

        List<IslemLog> kayitlar = (tip != null && !tip.isBlank())
                ? islemLogRepository.findByIslemTipiOrderByIslemZamaniDesc(tip.trim(), page)
                : islemLogRepository.findAllByOrderByIslemZamaniDesc(page);

        return kayitlar.stream().map(this::toDto).toList();
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void basarisizGirisKaydet(Kullanici kullanici, String denenenKullaniciAdi, String detay) {
        IslemLog log = new IslemLog();
        log.setKullanici(kullanici);
        log.setDenenenKullaniciAdi(denenenKullaniciAdi);
        log.setIslemTipi("GIRIS_BASARISIZ");
        log.setIslemZamani(LocalDateTime.now());
        log.setDetay(detay);
        islemLogRepository.save(log);
    }

    @Transactional(propagation = Propagation.REQUIRED)
    public void basariliGirisKaydet(IslemLog log) {
        islemLogRepository.save(log);
    }

    private IslemLogDTO toDto(IslemLog log) {
        Kullanici kullanici = log.getKullanici();
        String kullaniciAdi = kullanici != null
                ? kullanici.getKullaniciAdi()
                : (log.getDenenenKullaniciAdi() != null ? log.getDenenenKullaniciAdi() : "bilinmiyor");
        String adSoyad = kullanici != null ? kullanici.getAdSoyad() : "Bilinmeyen kullanici";

        return new IslemLogDTO(
                log.getId(),
                kullanici != null ? kullanici.getId() : null,
                kullaniciAdi,
                adSoyad,
                log.getIslemTipi(),
                log.getIlgiliIhlal() != null ? log.getIlgiliIhlal().getId() : null,
                log.getIslemZamani(),
                log.getDetay()
        );
    }
}
