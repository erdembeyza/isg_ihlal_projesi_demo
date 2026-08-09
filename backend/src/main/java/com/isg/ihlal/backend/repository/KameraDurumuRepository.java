package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.KameraDurumu;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface KameraDurumuRepository extends JpaRepository<KameraDurumu, Long> {

    Optional<KameraDurumu> findByBolgeIdAndKameraAdi(Long bolgeId, String kameraAdi);

    List<KameraDurumu> findByBolgeId(Long bolgeId);

    List<KameraDurumu> findByBolgeIdIn(Collection<Long> bolgeIds);

    List<KameraDurumu> findAllByOrderByBolgeIdAscKameraAdiAsc();
}
