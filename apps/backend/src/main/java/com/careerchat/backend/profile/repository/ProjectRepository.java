package com.careerchat.backend.profile.repository;

import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.domain.Project;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProjectRepository extends JpaRepository<Project, Long> {

    List<Project> findAllByProfileOrderByIdAsc(Profile profile);

    void deleteAllByProfile(Profile profile);
}
