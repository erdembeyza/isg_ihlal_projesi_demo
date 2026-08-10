package com.isg.ihlal.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

/**
 * TABLO: personel_yuzleri
 * Kisi tanima icin personelin referans yuz fotograflari.
 */
@Entity
@Table(name = "personel_yuzleri")
public class PersonelYuzu {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "personel_id", nullable = false)
    private Personel personel;

    @NotBlank
    @Size(max = 500)
    @Column(name = "foto_yolu", nullable = false, length = 500)
    private String fotoYolu;

    @NotNull
    @Column(name = "olusturma_zamani", nullable = false)
    private LocalDateTime olusturmaZamani;

    public PersonelYuzu() {
    }

    @PrePersist
    void olusturmaZamaniniAyarla() {
        if (olusturmaZamani == null) {
            olusturmaZamani = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Personel getPersonel() {
        return personel;
    }

    public void setPersonel(Personel personel) {
        this.personel = personel;
    }

    public String getFotoYolu() {
        return fotoYolu;
    }

    public void setFotoYolu(String fotoYolu) {
        this.fotoYolu = fotoYolu;
    }

    public LocalDateTime getOlusturmaZamani() {
        return olusturmaZamani;
    }

    public void setOlusturmaZamani(LocalDateTime olusturmaZamani) {
        this.olusturmaZamani = olusturmaZamani;
    }
}
