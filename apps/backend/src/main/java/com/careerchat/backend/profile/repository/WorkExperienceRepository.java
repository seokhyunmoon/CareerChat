package com.careerchat.backend.profile.repository;

import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.domain.WorkExperience;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkExperienceRepository extends JpaRepository<WorkExperience, Long> {

    List<WorkExperience> findAllByProfileOrderByIdAsc(Profile profile);

    void deleteAllByProfile(Profile profile);
}
