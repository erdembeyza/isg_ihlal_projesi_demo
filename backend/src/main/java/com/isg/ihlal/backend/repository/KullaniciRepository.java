package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Kullanici;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface KullaniciRepository extends JpaRepository<Kullanici, Long> {

    /**
     * MODUL-3 (JWT Security): /api/auth/login ucunda kullanici adi/sifre
     * dogrulamasi icin kullanilir.
     */
    Optional<Kullanici> findByKullaniciAdi(String kullaniciAdi);

    boolean existsByKullaniciAdi(String kullaniciAdi);
}
