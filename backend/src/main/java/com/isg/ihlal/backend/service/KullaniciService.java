package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.KullaniciGuncelleRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciRequestDTO;
import com.isg.ihlal.backend.dto.KullaniciResponseDTO;
import com.isg.ihlal.backend.dto.ProfilGuncelleRequestDTO;
import com.isg.ihlal.backend.dto.ProfilResponseDTO;
import com.isg.ihlal.backend.dto.SifreDegistirRequestDTO;
import com.isg.ihlal.backend.dto.SifreGuncelleRequestDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.IslemLog;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.entity.Rol;
import com.isg.ihlal.backend.repository.BolgeRepository;
import com.isg.ihlal.backend.repository.IslemLogRepository;
import com.isg.ihlal.backend.repository.KullaniciRepository;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class KullaniciService {

    private final KullaniciRepository kullaniciRepository;
    private final BolgeRepository bolgeRepository;
    private final IslemLogRepository islemLogRepository;
    private final PasswordEncoder passwordEncoder;

    public KullaniciService(
            KullaniciRepository kullaniciRepository,
            BolgeRepository bolgeRepository,
            IslemLogRepository islemLogRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.kullaniciRepository = kullaniciRepository;
        this.bolgeRepository = bolgeRepository;
        this.islemLogRepository = islemLogRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public List<KullaniciResponseDTO> listele() {
        return kullaniciRepository.findAll().stream()
                .filter(k -> k.getRol() != Rol.AI_CORE_SERVIS)
                .sorted(Comparator.comparing(Kullanici::getAdSoyad, String.CASE_INSENSITIVE_ORDER))
                .map(this::toDto)
                .toList();
    }

    public ProfilResponseDTO profilGetir(AuthenticatedUser user) {
        return toProfilDto(bul(user.kullaniciId()));
    }

    @Transactional
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

        Bolge bolge = bolgeCozumle(dto.rol(), dto.bolgeId());

        Kullanici kullanici = new Kullanici();
        kullanici.setKullaniciAdi(dto.kullaniciAdi());
        kullanici.setSifreHash(passwordEncoder.encode(dto.sifre()));
        kullanici.setAdSoyad(dto.adSoyad());
        kullanici.setRol(dto.rol());
        kullanici.setBolge(bolge);
        kullanici.setAktifMi(Boolean.TRUE);

        return toDto(kullaniciRepository.save(kullanici));
    }

    @Transactional
    public KullaniciResponseDTO guncelle(Long id, KullaniciGuncelleRequestDTO dto, AuthenticatedUser yapan) {
        Kullanici kullanici = bul(id);
        servisHesabiKontrolu(kullanici);

        if (dto.rol() == Rol.AI_CORE_SERVIS) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "AI_CORE_SERVIS rolu atanamaz");
        }

        if (Boolean.FALSE.equals(dto.aktifMi()) && kullanici.getId().equals(yapan.kullaniciId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Kendi hesabinizi pasif yapamazsiniz");
        }

        String yeniKullaniciAdi = dto.kullaniciAdi().trim();
        if (kullaniciRepository.existsByKullaniciAdiAndIdNot(yeniKullaniciAdi, id)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Bu kullanici adi zaten kullanimda: " + yeniKullaniciAdi);
        }

        Bolge bolge = bolgeCozumle(dto.rol(), dto.bolgeId());

        kullanici.setKullaniciAdi(yeniKullaniciAdi);
        kullanici.setAdSoyad(dto.adSoyad().trim());
        kullanici.setRol(dto.rol());
        kullanici.setBolge(bolge);
        kullanici.setAktifMi(dto.aktifMi());
        kullanici.setEposta(bosMetin(dto.eposta()));
        kullanici.setTelefon(bosMetin(dto.telefon()));
        kullanici.setGorev(bosMetin(dto.gorev()));

        if (dto.yeniSifre() != null && !dto.yeniSifre().isBlank()) {
            String yeniSifre = dto.yeniSifre().trim();
            if (yeniSifre.length() < 6) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "yeniSifre en az 6 karakter olmalidir");
            }
            kullanici.setSifreHash(passwordEncoder.encode(yeniSifre));
        }

        Kullanici guncellenen = kullaniciRepository.save(kullanici);
        logYaz(yapan.kullaniciId(), "KULLANICI_GUNCELLEME", "Kullanici guncellendi: " + guncellenen.getKullaniciAdi());

        return toDto(guncellenen);
    }

    @Transactional
    public void sifreGuncelle(Long id, SifreGuncelleRequestDTO dto, AuthenticatedUser yapan) {
        Kullanici kullanici = bul(id);
        servisHesabiKontrolu(kullanici);

        kullanici.setSifreHash(passwordEncoder.encode(dto.yeniSifre()));
        kullaniciRepository.save(kullanici);
        logYaz(yapan.kullaniciId(), "SIFRE_GUNCELLEME", "Sifre guncellendi: " + kullanici.getKullaniciAdi());
    }

    @Transactional
    public ProfilResponseDTO profilGuncelle(AuthenticatedUser user, ProfilGuncelleRequestDTO dto) {
        Kullanici kullanici = bul(user.kullaniciId());
        kullanici.setAdSoyad(dto.adSoyad().trim());
        Kullanici guncellenen = kullaniciRepository.save(kullanici);
        logYaz(user.kullaniciId(), "PROFIL_GUNCELLEME", "Profil ad soyad guncellendi");
        return toProfilDto(guncellenen);
    }

    @Transactional
    public void sifreDegistir(AuthenticatedUser user, SifreDegistirRequestDTO dto) {
        Kullanici kullanici = bul(user.kullaniciId());

        if (!passwordEncoder.matches(dto.mevcutSifre(), kullanici.getSifreHash())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Mevcut sifre hatali");
        }

        if (dto.mevcutSifre().equals(dto.yeniSifre())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Yeni sifre mevcut sifreden farkli olmalidir");
        }

        kullanici.setSifreHash(passwordEncoder.encode(dto.yeniSifre()));
        kullaniciRepository.save(kullanici);
        logYaz(user.kullaniciId(), "SIFRE_DEGISTIRME", "Kullanici kendi sifresini degistirdi");
    }

    private Kullanici bul(Long id) {
        return kullaniciRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Kullanici bulunamadi: " + id));
    }

    private void servisHesabiKontrolu(Kullanici kullanici) {
        if (kullanici.getRol() == Rol.AI_CORE_SERVIS) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Servis hesabi duzenlenemez");
        }
    }

    private Bolge bolgeCozumle(Rol rol, Long bolgeId) {
        if (rol == Rol.FORMEN) {
            if (bolgeId == null) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "FORMEN rolu icin bolgeId zorunludur");
            }
            return bolgeRepository.findById(bolgeId)
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Bolge bulunamadi: " + bolgeId));
        }
        return null;
    }

    private void logYaz(Long kullaniciId, String islemTipi, String detay) {
        Kullanici yapan = bul(kullaniciId);
        IslemLog log = new IslemLog();
        log.setKullanici(yapan);
        log.setIslemTipi(islemTipi);
        log.setIslemZamani(LocalDateTime.now());
        log.setDetay(detay);
        islemLogRepository.save(log);
    }

    private KullaniciResponseDTO toDto(Kullanici kullanici) {
        Bolge bolge = kullanici.getBolge();
        return new KullaniciResponseDTO(
                kullanici.getId(),
                kullanici.getKullaniciAdi(),
                kullanici.getAdSoyad(),
                kullanici.getRol().name(),
                bolge != null ? bolge.getId() : null,
                bolge != null ? bolge.getBolgeAdi() : null,
                kullanici.getAktifMi(),
                kullanici.getEposta(),
                kullanici.getTelefon(),
                kullanici.getGorev()
        );
    }

    private static String bosMetin(String deger) {
        if (deger == null) {
            return null;
        }
        String temiz = deger.trim();
        return temiz.isEmpty() ? null : temiz;
    }

    private ProfilResponseDTO toProfilDto(Kullanici kullanici) {
        Bolge bolge = kullanici.getBolge();
        var sonGiris = islemLogRepository
                .findFirstByKullaniciIdAndIslemTipiOrderByIslemZamaniDesc(kullanici.getId(), "GIRIS")
                .map(IslemLog::getIslemZamani)
                .orElse(null);

        return new ProfilResponseDTO(
                kullanici.getId(),
                kullanici.getKullaniciAdi(),
                kullanici.getAdSoyad(),
                kullanici.getRol().name(),
                bolge != null ? bolge.getId() : null,
                bolge != null ? bolge.getBolgeAdi() : null,
                kullanici.getAktifMi(),
                kullanici.getEposta(),
                kullanici.getTelefon(),
                kullanici.getGorev(),
                sonGiris
        );
    }
}
