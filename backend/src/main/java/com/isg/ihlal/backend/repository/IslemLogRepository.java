package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.IslemLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface IslemLogRepository extends JpaRepository<IslemLog, Long> {

    List<IslemLog> findByKullaniciId(Long kullaniciId);

    List<IslemLog> findByIlgiliIhlalId(Long ihlalId);
}
