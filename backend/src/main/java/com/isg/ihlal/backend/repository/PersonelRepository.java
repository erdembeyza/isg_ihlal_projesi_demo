package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Personel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PersonelRepository extends JpaRepository<Personel, Long> {

    Optional<Personel> findBySicilNo(String sicilNo);

    List<Personel> findByBolgeId(Long bolgeId);
}
