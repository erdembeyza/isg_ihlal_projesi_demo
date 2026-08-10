package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.PersonelDTO;
import com.isg.ihlal.backend.dto.PersonelGaleriDTO;
import com.isg.ihlal.backend.dto.PersonelGaleriYuzDTO;
import com.isg.ihlal.backend.dto.PersonelRequestDTO;
import com.isg.ihlal.backend.dto.PersonelYuzDTO;
import com.isg.ihlal.backend.dto.YuzYukleRequestDTO;
import com.isg.ihlal.backend.entity.Bolge;
import com.isg.ihlal.backend.entity.Personel;
import com.isg.ihlal.backend.entity.PersonelYuzu;
import com.isg.ihlal.backend.repository.BolgeRepository;
import com.isg.ihlal.backend.repository.PersonelRepository;
import com.isg.ihlal.backend.repository.PersonelYuzuRepository;
import com.isg.ihlal.backend.storage.FileStorageService;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class PersonelService {

    private static final int MAX_YUZ_PERSONEL = 5;

    private final PersonelRepository personelRepository;
    private final PersonelYuzuRepository personelYuzuRepository;
    private final BolgeRepository bolgeRepository;
    private final FileStorageService fileStorageService;

    public PersonelService(
            PersonelRepository personelRepository,
            PersonelYuzuRepository personelYuzuRepository,
            BolgeRepository bolgeRepository,
            FileStorageService fileStorageService
    ) {
        this.personelRepository = personelRepository;
        this.personelYuzuRepository = personelYuzuRepository;
        this.bolgeRepository = bolgeRepository;
        this.fileStorageService = fileStorageService;
    }

    @Transactional(readOnly = true)
    public List<PersonelDTO> listele() {
        return personelRepository.findAll().stream()
                .sorted((a, b) -> a.getSicilNo().compareToIgnoreCase(b.getSicilNo()))
                .map(this::toDto)
                .toList();
    }

    @Transactional
    public PersonelDTO olustur(PersonelRequestDTO dto) {
        String sicil = dto.sicilNo().trim();
        if (personelRepository.findBySicilNo(sicil).isPresent()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Sicil no zaten kayitli: " + sicil);
        }
        Personel personel = new Personel();
        alanlariUygula(personel, dto, sicil);
        return toDto(personelRepository.save(personel));
    }

    @Transactional
    public PersonelDTO guncelle(Long id, PersonelRequestDTO dto) {
        Personel personel = personelBul(id);
        String sicil = dto.sicilNo().trim();
        personelRepository.findBySicilNo(sicil)
                .filter(p -> !p.getId().equals(id))
                .ifPresent(p -> {
                    throw new ResponseStatusException(HttpStatus.CONFLICT, "Sicil no zaten kayitli: " + sicil);
                });
        alanlariUygula(personel, dto, sicil);
        return toDto(personelRepository.save(personel));
    }

    @Transactional
    public PersonelYuzDTO yuzEkle(Long personelId, YuzYukleRequestDTO dto) {
        Personel personel = personelBul(personelId);
        long mevcut = personelYuzuRepository.countByPersonelId(personelId);
        if (mevcut >= MAX_YUZ_PERSONEL) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Bir personel icin en fazla " + MAX_YUZ_PERSONEL + " yuz fotografi yuklenebilir"
            );
        }
        String fotoYolu = fileStorageService.personelYuzuKaydet(dto.fotoBase64(), personelId);
        PersonelYuzu yuz = new PersonelYuzu();
        yuz.setPersonel(personel);
        yuz.setFotoYolu(fotoYolu);
        PersonelYuzu kayit = personelYuzuRepository.save(yuz);
        return new PersonelYuzDTO(kayit.getId(), kayit.getFotoYolu(), kayit.getOlusturmaZamani());
    }

    @Transactional
    public void yuzSil(Long yuzId) {
        PersonelYuzu yuz = personelYuzuRepository.findById(yuzId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Yuz kaydi bulunamadi"));
        String fotoYolu = yuz.getFotoYolu();
        personelYuzuRepository.delete(yuz);
        fileStorageService.fotoSil(fotoYolu);
    }

    /**
     * AI Core icin aktif personellerin yuz galerisi (base64).
     */
    @Transactional(readOnly = true)
    public List<PersonelGaleriDTO> galeri() {
        List<PersonelYuzu> yuzler = personelYuzuRepository.findByPersonelAktifMiTrue();
        Map<Long, PersonelGaleriDTO> harita = new LinkedHashMap<>();

        for (PersonelYuzu yuz : yuzler) {
            Personel p = yuz.getPersonel();
            PersonelGaleriDTO mevcut = harita.get(p.getId());
            if (mevcut == null) {
                mevcut = new PersonelGaleriDTO(
                        p.getId(),
                        p.getSicilNo(),
                        p.getAdSoyad(),
                        new ArrayList<>()
                );
                harita.put(p.getId(), mevcut);
            }
            String base64;
            try {
                base64 = fileStorageService.fotoBase64Oku(yuz.getFotoYolu());
            } catch (ResponseStatusException ex) {
                continue;
            }
            mevcut.yuzler().add(new PersonelGaleriYuzDTO(yuz.getId(), base64));
        }

        return harita.values().stream()
                .filter(g -> !g.yuzler().isEmpty())
                .toList();
    }

    private void alanlariUygula(Personel personel, PersonelRequestDTO dto, String sicil) {
        personel.setSicilNo(sicil);
        personel.setAdSoyad(dto.adSoyad().trim());
        personel.setDepartman(dto.departman() == null || dto.departman().isBlank()
                ? null
                : dto.departman().trim());
        personel.setAktifMi(dto.aktifMi() == null || dto.aktifMi());
        if (dto.bolgeId() == null) {
            personel.setBolge(null);
        } else {
            Bolge bolge = bolgeRepository.findById(dto.bolgeId())
                    .orElseThrow(() -> new ResponseStatusException(
                            HttpStatus.NOT_FOUND, "Bolge bulunamadi: " + dto.bolgeId()));
            personel.setBolge(bolge);
        }
    }

    private Personel personelBul(Long id) {
        return personelRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Personel bulunamadi: " + id));
    }

    private PersonelDTO toDto(Personel personel) {
        List<PersonelYuzDTO> yuzler = personelYuzuRepository.findByPersonelId(personel.getId()).stream()
                .map(y -> new PersonelYuzDTO(y.getId(), y.getFotoYolu(), y.getOlusturmaZamani()))
                .toList();
        Bolge bolge = personel.getBolge();
        return new PersonelDTO(
                personel.getId(),
                personel.getSicilNo(),
                personel.getAdSoyad(),
                personel.getDepartman(),
                bolge == null ? null : bolge.getId(),
                bolge == null ? null : bolge.getBolgeAdi(),
                personel.getAktifMi(),
                yuzler.size(),
                yuzler
        );
    }
}
