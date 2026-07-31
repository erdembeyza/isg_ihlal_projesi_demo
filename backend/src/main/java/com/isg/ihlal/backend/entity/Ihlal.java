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
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

/**
 * TABLO-4 : ihlaller
 * AI Core tarafindan tespit edilen her bir KDD ihlalinin kanit fotograflari, konumu,
 * zamani ve inceleme durumu ile kaydedildigi sistemin ana islem (transactional) tablosu.
 */
@Entity
@Table(name = "ihlaller")
public class Ihlal {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "bolge_id", nullable = false)
    private Bolge bolge;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "ihlal_tipi_id", nullable = false)
    private IhlalTipi ihlalTipi;

    @NotNull
    @Column(name = "tespit_zamani", nullable = false)
    private LocalDateTime tespitZamani;

    @NotBlank
    @Size(max = 500)
    @Column(name = "orijinal_foto_yolu", nullable = false, length = 500)
    private String orijinalFotoYolu;

    @NotBlank
    @Size(max = 500)
    @Column(name = "blurlu_foto_yolu", nullable = false, length = 500)
    private String blurluFotoYolu;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "durum", nullable = false, length = 20)
    private IhlalDurumu durum = IhlalDurumu.AKTIF;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reddeden_kullanici_id")
    private Kullanici reddedenKullanici;

    @Column(name = "red_zamani")
    private LocalDateTime redZamani;

    @Column(name = "olusturma_zamani", nullable = false, updatable = false)
    private LocalDateTime olusturmaZamani;

    public Ihlal() {
    }

    @PrePersist
    protected void varsayilanlariAta() {
        if (durum == null) {
            durum = IhlalDurumu.AKTIF;
        }
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

    public Bolge getBolge() {
        return bolge;
    }

    public void setBolge(Bolge bolge) {
        this.bolge = bolge;
    }

    public IhlalTipi getIhlalTipi() {
        return ihlalTipi;
    }

    public void setIhlalTipi(IhlalTipi ihlalTipi) {
        this.ihlalTipi = ihlalTipi;
    }

    public LocalDateTime getTespitZamani() {
        return tespitZamani;
    }

    public void setTespitZamani(LocalDateTime tespitZamani) {
        this.tespitZamani = tespitZamani;
    }

    public String getOrijinalFotoYolu() {
        return orijinalFotoYolu;
    }

    public void setOrijinalFotoYolu(String orijinalFotoYolu) {
        this.orijinalFotoYolu = orijinalFotoYolu;
    }

    public String getBlurluFotoYolu() {
        return blurluFotoYolu;
    }

    public void setBlurluFotoYolu(String blurluFotoYolu) {
        this.blurluFotoYolu = blurluFotoYolu;
    }

    public IhlalDurumu getDurum() {
        return durum;
    }

    public void setDurum(IhlalDurumu durum) {
        this.durum = durum;
    }

    public Kullanici getReddedenKullanici() {
        return reddedenKullanici;
    }

    public void setReddedenKullanici(Kullanici reddedenKullanici) {
        this.reddedenKullanici = reddedenKullanici;
    }

    public LocalDateTime getRedZamani() {
        return redZamani;
    }

    public void setRedZamani(LocalDateTime redZamani) {
        this.redZamani = redZamani;
    }

    public LocalDateTime getOlusturmaZamani() {
        return olusturmaZamani;
    }

    public void setOlusturmaZamani(LocalDateTime olusturmaZamani) {
        this.olusturmaZamani = olusturmaZamani;
    }
}
