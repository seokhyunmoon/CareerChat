package com.careerchat.backend.profile.repository;

import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileRepository extends JpaRepository<Profile, Long> {

    Optional<Profile> findByUser(User user);

    boolean existsByUser(User user);
}
