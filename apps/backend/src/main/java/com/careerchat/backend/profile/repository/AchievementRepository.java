package com.careerchat.backend.profile.repository;

import com.careerchat.backend.profile.domain.Achievement;
import com.careerchat.backend.profile.domain.Profile;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AchievementRepository extends JpaRepository<Achievement, Long> {

    List<Achievement> findAllByProfileOrderByIdAsc(Profile profile);

    void deleteAllByProfile(Profile profile);
}
