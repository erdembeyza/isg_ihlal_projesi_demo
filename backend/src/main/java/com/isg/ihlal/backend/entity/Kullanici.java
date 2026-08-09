package com.isg.ihlal.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.LinkedHashSet;
import java.util.Set;

/**
 * TABLO-3 : kullanicilar
 * Sisteme giris yapacak ISG yoneticisi ve formen rolundeki kurumsal personeli tutan tablo.
 * bolge / bolgeler alanlari yalnizca FORMEN rolu icin doludur.
 * Bir formen birden fazla bolgeye (kullanici_bolgeler) baglanabilir.
 */
@Entity
@Table(name = "kullanicilar")
public class Kullanici {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 50)
    @Column(name = "kullanici_adi", nullable = false, unique = true, length = 50)
    private String kullaniciAdi;

    @NotBlank
    @Size(max = 255)
    @Column(name = "sifre_hash", nullable = false, length = 255)
    private String sifreHash;

    @NotBlank
    @Size(max = 100)
    @Column(name = "ad_soyad", nullable = false, length = 100)
    private String adSoyad;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "rol", nullable = false, length = 20)
    private Rol rol;

    /** Birincil bolge (geriye donuk); coklu erisim icin {@link #bolgeler}. */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "bolge_id")
    private Bolge bolge;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "kullanici_bolgeler",
            joinColumns = @JoinColumn(name = "kullanici_id"),
            inverseJoinColumns = @JoinColumn(name = "bolge_id")
    )
    private Set<Bolge> bolgeler = new LinkedHashSet<>();

    @NotNull
    @Column(name = "aktif_mi", nullable = false)
    private Boolean aktifMi = Boolean.TRUE;

    @Size(max = 120)
    @Column(name = "eposta", length = 120)
    private String eposta;

    @Size(max = 30)
    @Column(name = "telefon", length = 30)
    private String telefon;

    @Size(max = 150)
    @Column(name = "gorev", length = 150)
    private String gorev;

    public Kullanici() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getKullaniciAdi() {
        return kullaniciAdi;
    }

    public void setKullaniciAdi(String kullaniciAdi) {
        this.kullaniciAdi = kullaniciAdi;
    }

    public String getSifreHash() {
        return sifreHash;
    }

    public void setSifreHash(String sifreHash) {
        this.sifreHash = sifreHash;
    }

    public String getAdSoyad() {
        return adSoyad;
    }

    public void setAdSoyad(String adSoyad) {
        this.adSoyad = adSoyad;
    }

    public Rol getRol() {
        return rol;
    }

    public void setRol(Rol rol) {
        this.rol = rol;
    }

    public Bolge getBolge() {
        return bolge;
    }

    public void setBolge(Bolge bolge) {
        this.bolge = bolge;
    }

    public Set<Bolge> getBolgeler() {
        return bolgeler;
    }

    public void setBolgeler(Set<Bolge> bolgeler) {
        this.bolgeler = bolgeler != null ? bolgeler : new LinkedHashSet<>();
    }

    public Boolean getAktifMi() {
        return aktifMi;
    }

    public void setAktifMi(Boolean aktifMi) {
        this.aktifMi = aktifMi;
    }

    public String getEposta() {
        return eposta;
    }

    public void setEposta(String eposta) {
        this.eposta = eposta;
    }

    public String getTelefon() {
        return telefon;
    }

    public void setTelefon(String telefon) {
        this.telefon = telefon;
    }

    public String getGorev() {
        return gorev;
    }

    public void setGorev(String gorev) {
        this.gorev = gorev;
    }
}
