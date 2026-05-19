package com.careerchat.backend.profile.repository;

import com.careerchat.backend.profile.domain.Education;
import com.careerchat.backend.profile.domain.Profile;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EducationRepository extends JpaRepository<Education, Long> {

    List<Education> findAllByProfileOrderByIdAsc(Profile profile);

    void deleteAllByProfile(Profile profile);
}
