package com.isg.ihlal.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * TABLO-2 : ihlal_tipleri
 * Tespit edilebilecek KDD ihlal tiplerini tanimlayan referans/lookup tablosu (BARET/YELEK/GOZLUK).
 */
@Entity
@Table(name = "ihlal_tipleri")
public class IhlalTipi {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Short id;

    @NotBlank
    @Size(max = 50)
    @Column(name = "tip_adi", nullable = false, length = 50)
    private String tipAdi;

    @Size(max = 255)
    @Column(name = "aciklama", length = 255)
    private String aciklama;

    public IhlalTipi() {
    }

    public IhlalTipi(String tipAdi, String aciklama) {
        this.tipAdi = tipAdi;
        this.aciklama = aciklama;
    }

    public Short getId() {
        return id;
    }

    public void setId(Short id) {
        this.id = id;
    }

    public String getTipAdi() {
        return tipAdi;
    }

    public void setTipAdi(String tipAdi) {
        this.tipAdi = tipAdi;
    }

    public String getAciklama() {
        return aciklama;
    }

    public void setAciklama(String aciklama) {
        this.aciklama = aciklama;
    }
}
