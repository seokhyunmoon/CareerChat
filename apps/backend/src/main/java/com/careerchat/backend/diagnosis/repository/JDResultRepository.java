package com.careerchat.backend.diagnosis.repository;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface JDResultRepository extends JpaRepository<JDResult, Long> {

    List<JDResult> findAllByDiagnosisOrderByDisplayOrderAsc(Diagnosis diagnosis);
}