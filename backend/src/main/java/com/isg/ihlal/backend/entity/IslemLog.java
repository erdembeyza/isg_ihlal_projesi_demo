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
 * TABLO-5 : islem_loglari
 * Kullanicilarin sistem uzerinde gerceklestirdigi kritik islemleri (giris, ihlal
 * reddetme vb.) izlenebilirlik ve denetim amaciyla kaydeden log tablosu.
 */
@Entity
@Table(name = "islem_loglari")
public class IslemLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "kullanici_id")
    private Kullanici kullanici;

    @Size(max = 50)
    @Column(name = "denenen_kullanici_adi", length = 50)
    private String denenenKullaniciAdi;

    @NotBlank
    @Size(max = 50)
    @Column(name = "islem_tipi", nullable = false, length = 50)
    private String islemTipi;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ilgili_ihlal_id")
    private Ihlal ilgiliIhlal;

    @NotNull
    @Column(name = "islem_zamani", nullable = false)
    private LocalDateTime islemZamani;

    @Size(max = 255)
    @Column(name = "detay", length = 255)
    private String detay;

    public IslemLog() {
    }

    @PrePersist
    protected void varsayilanlariAta() {
        if (islemZamani == null) {
            islemZamani = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Kullanici getKullanici() {
        return kullanici;
    }

    public void setKullanici(Kullanici kullanici) {
        this.kullanici = kullanici;
    }

    public String getIslemTipi() {
        return islemTipi;
    }

    public void setIslemTipi(String islemTipi) {
        this.islemTipi = islemTipi;
    }

    public Ihlal getIlgiliIhlal() {
        return ilgiliIhlal;
    }

    public void setIlgiliIhlal(Ihlal ilgiliIhlal) {
        this.ilgiliIhlal = ilgiliIhlal;
    }

    public LocalDateTime getIslemZamani() {
        return islemZamani;
    }

    public void setIslemZamani(LocalDateTime islemZamani) {
        this.islemZamani = islemZamani;
    }

    public String getDetay() {
        return detay;
    }

    public void setDetay(String detay) {
        this.detay = detay;
    }

    public String getDenenenKullaniciAdi() {
        return denenenKullaniciAdi;
    }

    public void setDenenenKullaniciAdi(String denenenKullaniciAdi) {
        this.denenenKullaniciAdi = denenenKullaniciAdi;
    }
}
