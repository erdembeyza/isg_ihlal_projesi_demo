package com.isg.ihlal.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * TABLO-6 : personeller
 * Saha calisanlarini (ad soyad, sicil no, departman) tutan referans tablosu.
 * Sistem kullanicilarindan (kullanicilar) bagimsizdir; ihlal kayitlarina
 * personel_id ile baglanir.
 */
@Entity
@Table(name = "personeller")
public class Personel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 50)
    @Column(name = "sicil_no", nullable = false, length = 50, unique = true)
    private String sicilNo;

    @NotBlank
    @Size(max = 100)
    @Column(name = "ad_soyad", nullable = false, length = 100)
    private String adSoyad;

    @Size(max = 100)
    @Column(name = "departman", length = 100)
    private String departman;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "bolge_id")
    private Bolge bolge;

    @NotNull
    @Column(name = "aktif_mi", nullable = false)
    private Boolean aktifMi = true;

    public Personel() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSicilNo() {
        return sicilNo;
    }

    public void setSicilNo(String sicilNo) {
        this.sicilNo = sicilNo;
    }

    public String getAdSoyad() {
        return adSoyad;
    }

    public void setAdSoyad(String adSoyad) {
        this.adSoyad = adSoyad;
    }

    public String getDepartman() {
        return departman;
    }

    public void setDepartman(String departman) {
        this.departman = departman;
    }

    public Bolge getBolge() {
        return bolge;
    }

    public void setBolge(Bolge bolge) {
        this.bolge = bolge;
    }

    public Boolean getAktifMi() {
        return aktifMi;
    }

    public void setAktifMi(Boolean aktifMi) {
        this.aktifMi = aktifMi;
    }
}
