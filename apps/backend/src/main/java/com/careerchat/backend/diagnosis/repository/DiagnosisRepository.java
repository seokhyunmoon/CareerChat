package com.careerchat.backend.diagnosis.repository;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.profile.domain.Profile;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DiagnosisRepository extends JpaRepository<Diagnosis, Long> {

    List<Diagnosis> findAllByProfileOrderByCreatedAtDescIdDesc(Profile profile);
}
