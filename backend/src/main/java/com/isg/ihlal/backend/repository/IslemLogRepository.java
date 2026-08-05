package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.IslemLog;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface IslemLogRepository extends JpaRepository<IslemLog, Long> {

    List<IslemLog> findByKullaniciId(Long kullaniciId);

    List<IslemLog> findByIlgiliIhlalId(Long ihlalId);

    List<IslemLog> findAllByOrderByIslemZamaniDesc(Pageable pageable);

    List<IslemLog> findByIslemTipiOrderByIslemZamaniDesc(String islemTipi, Pageable pageable);

    Optional<IslemLog> findFirstByKullaniciIdAndIslemTipiOrderByIslemZamaniDesc(
            Long kullaniciId,
            String islemTipi
    );
}
