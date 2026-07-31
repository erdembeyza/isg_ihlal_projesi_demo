package com.isg.ihlal.backend.repository;

import com.isg.ihlal.backend.entity.IhlalTipi;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface IhlalTipiRepository extends JpaRepository<IhlalTipi, Short> {
}
