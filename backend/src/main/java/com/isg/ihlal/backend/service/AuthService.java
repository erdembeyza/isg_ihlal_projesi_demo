package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.LoginRequestDTO;
import com.isg.ihlal.backend.dto.LoginResponseDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.IslemLog;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.repository.KullaniciRepository;
import com.isg.ihlal.backend.security.JwtService;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

@Service
public class AuthService {

    private final KullaniciRepository kullaniciRepository;
    private final IslemLogService islemLogService;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(
            KullaniciRepository kullaniciRepository,
            IslemLogService islemLogService,
            PasswordEncoder passwordEncoder,
            JwtService jwtService
    ) {
        this.kullaniciRepository = kullaniciRepository;
        this.islemLogService = islemLogService;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Transactional
    public LoginResponseDTO login(LoginRequestDTO request) {
        String denenenKullaniciAdi = request.kullaniciAdi().trim();
        Optional<Kullanici> kullaniciOpt = kullaniciRepository.findByKullaniciAdiWithBolgeler(denenenKullaniciAdi);

        if (kullaniciOpt.isEmpty()) {
            islemLogService.basarisizGirisKaydet(null, denenenKullaniciAdi, "Bilinmeyen kullanici adi");
            throw new BadCredentialsException("Kullanici adi veya sifre hatali");
        }

        Kullanici kullanici = kullaniciOpt.get();

        if (Boolean.FALSE.equals(kullanici.getAktifMi())) {
            islemLogService.basarisizGirisKaydet(kullanici, denenenKullaniciAdi, "Pasif hesap");
            throw new BadCredentialsException("Kullanici pasif durumda");
        }

        if (!passwordEncoder.matches(request.sifre(), kullanici.getSifreHash())) {
            islemLogService.basarisizGirisKaydet(kullanici, denenenKullaniciAdi, "Yanlis parola");
            throw new BadCredentialsException("Kullanici adi veya sifre hatali");
        }

        IslemLog girisLog = new IslemLog();
        girisLog.setKullanici(kullanici);
        girisLog.setDenenenKullaniciAdi(denenenKullaniciAdi);
        girisLog.setIslemTipi("GIRIS");
        girisLog.setIslemZamani(LocalDateTime.now());
        girisLog.setDetay("Basarili giris");
        islemLogService.basariliGirisKaydet(girisLog);

        String token = jwtService.generateToken(kullanici);
        List<Long> bolgeIds = bolgeIdsTopla(kullanici);
        Long bolgeId = bolgeIds.isEmpty() ? null : bolgeIds.getFirst();

        return new LoginResponseDTO(
                token,
                kullanici.getId(),
                kullanici.getKullaniciAdi(),
                kullanici.getRol().name(),
                kullanici.getAdSoyad(),
                bolgeId,
                bolgeIds
        );
    }

    private static List<Long> bolgeIdsTopla(Kullanici kullanici) {
        Set<Long> ids = new LinkedHashSet<>();
        if (kullanici.getBolgeler() != null) {
            for (Bolge bolge : kullanici.getBolgeler()) {
                if (bolge != null && bolge.getId() != null) {
                    ids.add(bolge.getId());
                }
            }
        }
        if (kullanici.getBolge() != null && kullanici.getBolge().getId() != null) {
            ids.add(kullanici.getBolge().getId());
        }
        return new ArrayList<>(ids);
    }
}
