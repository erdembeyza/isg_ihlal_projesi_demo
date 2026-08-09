package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Kullanici;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface KullaniciRepository extends JpaRepository<Kullanici, Long> {

    Optional<Kullanici> findByKullaniciAdi(String kullaniciAdi);

    @Query("""
            SELECT DISTINCT k FROM Kullanici k
            LEFT JOIN FETCH k.bolge
            LEFT JOIN FETCH k.bolgeler
            WHERE k.kullaniciAdi = :kullaniciAdi
            """)
    Optional<Kullanici> findByKullaniciAdiWithBolgeler(@Param("kullaniciAdi") String kullaniciAdi);

    @Query("""
            SELECT DISTINCT k FROM Kullanici k
            LEFT JOIN FETCH k.bolge
            LEFT JOIN FETCH k.bolgeler
            WHERE k.id = :id
            """)
    Optional<Kullanici> findByIdWithBolgeler(@Param("id") Long id);

    boolean existsByKullaniciAdi(String kullaniciAdi);

    boolean existsByKullaniciAdiAndIdNot(String kullaniciAdi, Long id);
}
