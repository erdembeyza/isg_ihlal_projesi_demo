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
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

@Entity
@Table(name = "kamera_durumlari")
public class KameraDurumu {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "bolge_id", nullable = false)
    private Bolge bolge;

    @NotBlank
    @Size(max = 100)
    @Column(name = "kamera_adi", nullable = false, length = 100)
    private String kameraAdi;

    @NotNull
    @Column(name = "online_mi", nullable = false)
    private Boolean onlineMi = Boolean.TRUE;

    @Column(name = "son_kare_zamani")
    private LocalDateTime sonKareZamani;

    @Column(name = "fps")
    private Double fps;

    @NotNull
    @Column(name = "guncelleme_zamani", nullable = false)
    private LocalDateTime guncellemeZamani;

    public KameraDurumu() {
    }

    @PrePersist
    @PreUpdate
    protected void zamanlariAta() {
        if (guncellemeZamani == null) {
            guncellemeZamani = LocalDateTime.now();
        }
        if (onlineMi == null) {
            onlineMi = Boolean.TRUE;
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

    public String getKameraAdi() {
        return kameraAdi;
    }

    public void setKameraAdi(String kameraAdi) {
        this.kameraAdi = kameraAdi;
    }

    public Boolean getOnlineMi() {
        return onlineMi;
    }

    public void setOnlineMi(Boolean onlineMi) {
        this.onlineMi = onlineMi;
    }

    public LocalDateTime getSonKareZamani() {
        return sonKareZamani;
    }

    public void setSonKareZamani(LocalDateTime sonKareZamani) {
        this.sonKareZamani = sonKareZamani;
    }

    public Double getFps() {
        return fps;
    }

    public void setFps(Double fps) {
        this.fps = fps;
    }

    public LocalDateTime getGuncellemeZamani() {
        return guncellemeZamani;
    }

    public void setGuncellemeZamani(LocalDateTime guncellemeZamani) {
        this.guncellemeZamani = guncellemeZamani;
    }
}
