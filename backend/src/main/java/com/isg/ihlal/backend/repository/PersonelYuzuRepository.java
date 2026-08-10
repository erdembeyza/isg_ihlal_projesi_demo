package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.PersonelYuzu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PersonelYuzuRepository extends JpaRepository<PersonelYuzu, Long> {

    List<PersonelYuzu> findByPersonelId(Long personelId);

    List<PersonelYuzu> findByPersonelAktifMiTrue();

    long countByPersonelId(Long personelId);
}
