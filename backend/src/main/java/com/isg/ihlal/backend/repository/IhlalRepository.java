package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.Ihlal;
import com.isg.ihlal.backend.entity.IhlalDurumu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

@Repository
public interface IhlalRepository extends JpaRepository<Ihlal, Long> {

    /**
     * MODUL-2: GET /api/ihlaller ucunda FORMEN rolu icin rol bazli filtreleme
     * (WHERE bolge_id=...) bu metotla saglanir; ISG_YONETICI icin filtresiz
     * findAll() kullanilir.
     */
    List<Ihlal> findByBolgeId(Long bolgeId);

    List<Ihlal> findByBolgeIdIn(Collection<Long> bolgeIds);

    List<Ihlal> findByBolgeIdAndDurum(Long bolgeId, IhlalDurumu durum);

    List<Ihlal> findByBolgeIdInAndDurum(Collection<Long> bolgeIds, IhlalDurumu durum);

    List<Ihlal> findByDurum(IhlalDurumu durum);

    List<Ihlal> findByTespitZamaniBetween(LocalDateTime baslangic, LocalDateTime bitis);

    List<Ihlal> findByBolgeIdAndTespitZamaniBetween(Long bolgeId, LocalDateTime baslangic, LocalDateTime bitis);

    List<Ihlal> findByBolgeIdInAndTespitZamaniBetween(
            Collection<Long> bolgeIds, LocalDateTime baslangic, LocalDateTime bitis);

    long countByDurum(IhlalDurumu durum);

    long countByTespitZamaniBetween(LocalDateTime baslangic, LocalDateTime bitis);

    long countByDurumAndTespitZamaniBetween(IhlalDurumu durum, LocalDateTime baslangic, LocalDateTime bitis);
}
