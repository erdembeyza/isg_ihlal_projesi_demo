package com.isg.ihlal.backend.controller;

import com.isg.ihlal.backend.dto.PersonelDTO;
import com.isg.ihlal.backend.dto.PersonelGaleriDTO;
import com.isg.ihlal.backend.dto.PersonelRequestDTO;
import com.isg.ihlal.backend.dto.PersonelYuzDTO;
import com.isg.ihlal.backend.dto.YuzYukleRequestDTO;
import com.isg.ihlal.backend.service.PersonelService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/personeller")
public class PersonelController {

    private final PersonelService personelService;

    public PersonelController(PersonelService personelService) {
        this.personelService = personelService;
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ISG_YONETICI', 'FORMEN', 'GORUNTULEYICI')")
    public List<PersonelDTO> listele() {
        return personelService.listele();
    }

    /**
     * AI Core kisi tanima galerisi — yuz fotograflari base64.
     */
    @GetMapping("/galeri")
    @PreAuthorize("hasAnyRole('AI_CORE_SERVIS', 'ISG_YONETICI')")
    public List<PersonelGaleriDTO> galeri() {
        return personelService.galeri();
    }

    @PostMapping
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<PersonelDTO> olustur(@Valid @RequestBody PersonelRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(personelService.olustur(dto));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public PersonelDTO guncelle(@PathVariable Long id, @Valid @RequestBody PersonelRequestDTO dto) {
        return personelService.guncelle(id, dto);
    }

    @PostMapping("/{id}/yuzler")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<PersonelYuzDTO> yuzEkle(
            @PathVariable Long id,
            @Valid @RequestBody YuzYukleRequestDTO dto
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(personelService.yuzEkle(id, dto));
    }

    @DeleteMapping("/yuzler/{yuzId}")
    @PreAuthorize("hasRole('ISG_YONETICI')")
    public ResponseEntity<Void> yuzSil(@PathVariable Long yuzId) {
        personelService.yuzSil(yuzId);
        return ResponseEntity.noContent().build();
    }
}
