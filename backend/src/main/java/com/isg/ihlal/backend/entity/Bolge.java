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
 * TABLO-1 : bolgeler
 * Fabrika icindeki uretim bolgelerini (vardiya/departman) tanimlayan referans tablosu.
 */
@Entity
@Table(name = "bolgeler")
public class Bolge {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 100)
    @Column(name = "bolge_adi", nullable = false, length = 100)
    private String bolgeAdi;

    @Size(max = 255)
    @Column(name = "aciklama", length = 255)
    private String aciklama;

    public Bolge() {
    }

    public Bolge(String bolgeAdi, String aciklama) {
        this.bolgeAdi = bolgeAdi;
        this.aciklama = aciklama;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getBolgeAdi() {
        return bolgeAdi;
    }

    public void setBolgeAdi(String bolgeAdi) {
        this.bolgeAdi = bolgeAdi;
    }

    public String getAciklama() {
        return aciklama;
    }

    public void setAciklama(String aciklama) {
        this.aciklama = aciklama;
    }
}
