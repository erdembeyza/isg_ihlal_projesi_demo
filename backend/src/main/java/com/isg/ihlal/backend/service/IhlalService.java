package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.FinetuneHavuzSenkronDTO;
import com.isg.ihlal.backend.dto.IhlalIstatistikDTO;
import com.isg.ihlal.backend.dto.IhlalKayitRequestDTO;
import com.isg.ihlal.backend.dto.IhlalRedRequestDTO;
import com.isg.ihlal.backend.dto.IhlalResponseDTO;
import com.isg.ihlal.backend.dto.PersonelIstatistikDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.Ihlal;
import com.isg.ihlal.backend.entity.IhlalDurumu;
import com.isg.ihlal.backend.entity.IhlalTipi;
import com.isg.ihlal.backend.entity.IslemLog;
import com.isg.ihlal.backend.entity.Kullanici;
import com.isg.ihlal.backend.entity.Personel;
import com.isg.ihlal.backend.entity.Rol;
import com.isg.ihlal.backend.repository.BolgeRepository;
import com.isg.ihlal.backend.repository.IhlalRepository;
import com.isg.ihlal.backend.repository.IhlalTipiRepository;
import com.isg.ihlal.backend.repository.IslemLogRepository;
import com.isg.ihlal.backend.repository.KullaniciRepository;
import com.isg.ihlal.backend.repository.PersonelRepository;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.isg.ihlal.backend.storage.FileStorageService;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * MODUL-2 (tasarim_mimari.md): ihlal kayitlarinin olusturulmasi, rol bazli
 * listelenmesi/goruntulenmesi, reddedilmesi/cozumu ve istatistik hesaplamasi.
 *
 * Sinif genelinde @Transactional(readOnly = true): entity -> DTO donusumu
 * sirasinda bolge/ihlalTipi/personel gibi LAZY iliskilere erisildiginde Hibernate
 * session'inin acik kalmasini saglar (aksi halde LazyInitializationException
 * alinir, cunku application.yml'de open-in-view kapali).
 * Yazma yapan metotlar kendi @Transactional'lari ile override eder.
 */
@Service
@Transactional(readOnly = true)
public class IhlalService {

    private final IhlalRepository ihlalRepository;
    private final BolgeRepository bolgeRepository;
    private final IhlalTipiRepository ihlalTipiRepository;
    private final KullaniciRepository kullaniciRepository;
    private final IslemLogRepository islemLogRepository;
    private final PersonelRepository personelRepository;
    private final FileStorageService fileStorageService;

    public IhlalService(
            IhlalRepository ihlalRepository,
            BolgeRepository bolgeRepository,
            IhlalTipiRepository ihlalTipiRepository,
            KullaniciRepository kullaniciRepository,
            IslemLogRepository islemLogRepository,
            PersonelRepository personelRepository,
            FileStorageService fileStorageService
    ) {
        this.ihlalRepository = ihlalRepository;
        this.bolgeRepository = bolgeRepository;
        this.ihlalTipiRepository = ihlalTipiRepository;
        this.kullaniciRepository = kullaniciRepository;
        this.islemLogRepository = islemLogRepository;
        this.personelRepository = personelRepository;
        this.fileStorageService = fileStorageService;
    }

    @Transactional
    public IhlalResponseDTO kaydet(IhlalKayitRequestDTO dto) {
        Bolge bolge = bolgeRepository.findById(dto.bolgeId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Bolge bulunamadi: " + dto.bolgeId()));
        IhlalTipi ihlalTipi = ihlalTipiRepository.findById(dto.ihlalTipiId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Ihlal tipi bulunamadi: " + dto.ihlalTipiId()));

        String orijinalYol = fileStorageService.orijinalFotoKaydet(dto.orijinalFotoBase64());

        Ihlal ihlal = new Ihlal();
        ihlal.setBolge(bolge);
        ihlal.setIhlalTipi(ihlalTipi);
        ihlal.setTespitZamani(dto.tespitZamani());
        ihlal.setOrijinalFotoYolu(orijinalYol);
        ihlal.setDurum(IhlalDurumu.AKTIF);
        ihlal.setPersonel(personelCozumle(dto.personelId(), dto.personelSicilNo()));

        Ihlal kaydedilen = ihlalRepository.save(ihlal);

        return toDto(kaydedilen);
    }

    public List<IhlalResponseDTO> listele(AuthenticatedUser user) {
        List<Ihlal> ihlaller = isFormen(user)
                ? ihlalRepository.findByBolgeId(user.bolgeId())
                : ihlalRepository.findAll();

        return ihlaller.stream()
                .map(this::toDto)
                .toList();
    }

    public IhlalResponseDTO detay(Long id, AuthenticatedUser user) {
        Ihlal ihlal = bul(id);
        bolgeErisimKontrol(ihlal, user);
        return toDto(ihlal);
    }

    @Transactional
    public IhlalResponseDTO reddet(Long id, IhlalRedRequestDTO dto, AuthenticatedUser user) {
        Ihlal ihlal = bul(id);

        Kullanici yonetici = kullaniciRepository.findById(user.kullaniciId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Kullanici bulunamadi: " + user.kullaniciId()));

        ihlal.setDurum(IhlalDurumu.HATALI_TESPIT);
        ihlal.setReddedenKullanici(yonetici);
        ihlal.setRedZamani(LocalDateTime.now());
        Ihlal guncellenen = ihlalRepository.save(ihlal);

        IslemLog log = new IslemLog();
        log.setKullanici(yonetici);
        log.setIslemTipi("IHLAL_REDDETME");
        log.setIlgiliIhlal(guncellenen);
        log.setIslemZamani(LocalDateTime.now());
        log.setDetay(dto != null ? dto.redNedeni() : null);
        islemLogRepository.save(log);

        // MODUL-6: reddedilen orijinal kanit fine-tune havuzuna isaretlenir/kopyalanir.
        fileStorageService.finetuneHavuzunaKopyala(
                guncellenen.getOrijinalFotoYolu(),
                guncellenen.getId(),
                guncellenen.getIhlalTipi().getTipAdi()
        );

        return toDto(guncellenen);
    }

    /**
     * AKTIF ihlali COZULDU olarak isaretler. Formen yalnizca kendi bolgesindeki
     * kayitlari cozebilir; yonetici tum fabrika kayitlarini cozebilir.
     */
    @Transactional
    public IhlalResponseDTO coz(Long id, AuthenticatedUser user) {
        Ihlal ihlal = bul(id);
        bolgeErisimKontrol(ihlal, user);

        if (ihlal.getDurum() != IhlalDurumu.AKTIF) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Yalnizca AKTIF ihlaller cozulebilir");
        }

        Kullanici cozen = kullaniciRepository.findById(user.kullaniciId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Kullanici bulunamadi: " + user.kullaniciId()));

        ihlal.setDurum(IhlalDurumu.COZULDU);
        ihlal.setCozenKullanici(cozen);
        ihlal.setCozmeZamani(LocalDateTime.now());
        Ihlal guncellenen = ihlalRepository.save(ihlal);

        IslemLog log = new IslemLog();
        log.setKullanici(cozen);
        log.setIslemTipi("IHLAL_COZME");
        log.setIlgiliIhlal(guncellenen);
        log.setIslemZamani(LocalDateTime.now());
        log.setDetay("Ihlal cozuldu olarak isaretlendi");
        islemLogRepository.save(log);

        return toDto(guncellenen);
    }

    /**
     * Mevcut HATALI_TESPIT kayitlarinin orijinal fotolarini fine-tune havuzuna
     * geriye donuk kopyalar (idempotent).
     */
    @Transactional(readOnly = true)
    public FinetuneHavuzSenkronDTO finetuneHavuzunuSenkronizeEt() {
        List<Ihlal> reddedilenler = ihlalRepository.findByDurum(IhlalDurumu.HATALI_TESPIT);
        int kopyalanan = 0;
        int atlanan = 0;
        int hata = 0;

        for (Ihlal ihlal : reddedilenler) {
            try {
                boolean ok = fileStorageService.finetuneHavuzunaKopyala(
                        ihlal.getOrijinalFotoYolu(),
                        ihlal.getId(),
                        ihlal.getIhlalTipi().getTipAdi()
                );
                if (ok) {
                    kopyalanan++;
                } else {
                    atlanan++;
                }
            } catch (RuntimeException ex) {
                hata++;
            }
        }

        return new FinetuneHavuzSenkronDTO(reddedilenler.size(), kopyalanan, atlanan, hata);
    }

    public List<IhlalIstatistikDTO> istatistik(AuthenticatedUser user) {
        List<Ihlal> kapsam = isFormen(user)
                ? ihlalRepository.findByBolgeIdAndDurum(user.bolgeId(), IhlalDurumu.AKTIF)
                : ihlalRepository.findByDurum(IhlalDurumu.AKTIF);

        LocalDateTime simdi = LocalDateTime.now();
        LocalDateTime buHaftaBaslangic = simdi.minusDays(7);
        LocalDateTime oncekiHaftaBaslangic = simdi.minusDays(14);

        Map<Anahtar, Long> buHaftaSayim = kapsam.stream()
                .filter(i -> !i.getTespitZamani().isBefore(buHaftaBaslangic) && !i.getTespitZamani().isAfter(simdi))
                .collect(Collectors.groupingBy(Anahtar::of, Collectors.counting()));

        Map<Anahtar, Long> oncekiHaftaSayim = kapsam.stream()
                .filter(i -> !i.getTespitZamani().isBefore(oncekiHaftaBaslangic) && i.getTespitZamani().isBefore(buHaftaBaslangic))
                .collect(Collectors.groupingBy(Anahtar::of, Collectors.counting()));

        Set<Anahtar> tumAnahtarlar = new LinkedHashSet<>();
        tumAnahtarlar.addAll(buHaftaSayim.keySet());
        tumAnahtarlar.addAll(oncekiHaftaSayim.keySet());

        return tumAnahtarlar.stream()
                .map(anahtar -> {
                    long buHafta = buHaftaSayim.getOrDefault(anahtar, 0L);
                    long onceki = oncekiHaftaSayim.getOrDefault(anahtar, 0L);
                    double yuzde = yuzdeDegisimHesapla(buHafta, onceki);
                    return new IhlalIstatistikDTO(anahtar.bolgeAdi(), anahtar.ihlalTipiAdi(), (int) buHafta, yuzde);
                })
                .toList();
    }

    /**
     * Personel bazli ihlal analizi: toplam ihlal ve en cok ihlal edilen kategori.
     * HATALI_TESPIT kayitlari analize dahil edilmez.
     */
    public List<PersonelIstatistikDTO> personelIstatistik(AuthenticatedUser user) {
        List<Ihlal> kapsam = isFormen(user)
                ? ihlalRepository.findByBolgeId(user.bolgeId())
                : ihlalRepository.findAll();

        Map<Long, List<Ihlal>> personelGruplari = kapsam.stream()
                .filter(i -> i.getPersonel() != null)
                .filter(i -> i.getDurum() != IhlalDurumu.HATALI_TESPIT)
                .collect(Collectors.groupingBy(i -> i.getPersonel().getId(), LinkedHashMap::new, Collectors.toList()));

        return personelGruplari.values().stream()
                .map(liste -> {
                    Personel personel = liste.getFirst().getPersonel();
                    String enCokKategori = liste.stream()
                            .collect(Collectors.groupingBy(i -> i.getIhlalTipi().getTipAdi(), Collectors.counting()))
                            .entrySet().stream()
                            .max(Map.Entry.comparingByValue())
                            .map(Map.Entry::getKey)
                            .orElse("-");
                    return new PersonelIstatistikDTO(
                            personel.getId(),
                            personel.getAdSoyad(),
                            personel.getSicilNo(),
                            personel.getDepartman(),
                            liste.size(),
                            enCokKategori
                    );
                })
                .sorted(Comparator.comparingInt(PersonelIstatistikDTO::toplamIhlal).reversed())
                .toList();
    }

    private Personel personelCozumle(Long personelId, String sicilNo) {
        if (personelId != null) {
            return personelRepository.findById(personelId)
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Personel bulunamadi: " + personelId));
        }
        if (sicilNo != null && !sicilNo.isBlank()) {
            String aramaNo = sicilNo.trim();
            java.util.Optional<Personel> bulunan = personelRepository.findBySicilNoIgnoreCase(aramaNo);
            if (bulunan.isEmpty()) {
                // Yuz tanima etiketindeki alt cizgileri bosluga cevirip ad_soyad ile de dene (orn: "Beyza_Erdem" -> "Beyza Erdem")
                bulunan = personelRepository.findByAdSoyadIgnoreCase(aramaNo.replace("_", " "));
            }
            if (bulunan.isEmpty()) {
                org.slf4j.LoggerFactory.getLogger(IhlalService.class)
                        .warn("Yuz tanima sicil no veya ad soyad ile eslesmedi, personel atanmadi: '{}'", aramaNo);
                return null;
            }
            return bulunan.get();
        }
        return null;
    }

    private double yuzdeDegisimHesapla(long buHafta, long onceki) {
        if (onceki == 0) {
            return buHafta == 0 ? 0.0 : 100.0;
        }
        double yuzde = ((buHafta - onceki) * 100.0) / onceki;
        return Math.round(yuzde * 10.0) / 10.0;
    }

    private Ihlal bul(Long id) {
        return ihlalRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Ihlal bulunamadi: " + id));
    }

    private void bolgeErisimKontrol(Ihlal ihlal, AuthenticatedUser user) {
        if (isFormen(user) && !Objects.equals(ihlal.getBolge().getId(), user.bolgeId())) {
            throw new AccessDeniedException("Bu bolgeye ait ihlal kaydina erisim yetkiniz yok");
        }
    }

    private boolean isFormen(AuthenticatedUser user) {
        return Rol.FORMEN.name().equals(user.rol());
    }

    private IhlalResponseDTO toDto(Ihlal ihlal) {
        Personel personel = ihlal.getPersonel();
        return new IhlalResponseDTO(
                ihlal.getId(),
                ihlal.getBolge().getBolgeAdi(),
                ihlal.getIhlalTipi().getTipAdi(),
                ihlal.getTespitZamani(),
                ihlal.getOrijinalFotoYolu(),
                ihlal.getDurum().name(),
                personel != null ? personel.getId() : null,
                personel != null ? personel.getAdSoyad() : null,
                personel != null ? personel.getSicilNo() : null
        );
    }

    private record Anahtar(String bolgeAdi, String ihlalTipiAdi) {
        static Anahtar of(Ihlal ihlal) {
            return new Anahtar(ihlal.getBolge().getBolgeAdi(), ihlal.getIhlalTipi().getTipAdi());
        }
    }
}
