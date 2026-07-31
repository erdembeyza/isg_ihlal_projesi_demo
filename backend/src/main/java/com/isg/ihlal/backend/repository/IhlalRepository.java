package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Ihlal;
import com.isg.ihlal.backend.entity.IhlalDurumu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface IhlalRepository extends JpaRepository<Ihlal, Long> {

    /**
     * MODUL-2: GET /api/ihlaller ucunda FORMEN rolu icin rol bazli filtreleme
     * (WHERE bolge_id=...) bu metotla saglanir; ISG_YONETICI icin filtresiz
     * findAll() kullanilir.
     */
    List<Ihlal> findByBolgeId(Long bolgeId);

    List<Ihlal> findByBolgeIdAndDurum(Long bolgeId, IhlalDurumu durum);

    List<Ihlal> findByDurum(IhlalDurumu durum);
}
