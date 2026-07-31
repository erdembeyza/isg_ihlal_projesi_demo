package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Bolge;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BolgeRepository extends JpaRepository<Bolge, Long> {
}
