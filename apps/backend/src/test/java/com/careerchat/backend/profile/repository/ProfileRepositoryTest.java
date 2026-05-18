package com.careerchat.backend.profile.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.dao.DataIntegrityViolationException;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class ProfileRepositoryTest {

    private final ProfileRepository profileRepository;
    private final UserRepository userRepository;

    @Autowired
    ProfileRepositoryTest(ProfileRepository profileRepository, UserRepository userRepository) {
        this.profileRepository = profileRepository;
        this.userRepository = userRepository;
    }

    @Test
    void savesAndFindsByUser() {
        User user = userRepository.save(new User("profile@example.com", "hashed-password", "Moon", null));
        Profile profile = profileRepository.save(new Profile(user, ExperienceLevel.NEW));

        Profile found = profileRepository.findByUser(user).orElseThrow();

        assertThat(found.getId()).isEqualTo(profile.getId());
        assertThat(found.getUser().getId()).isEqualTo(user.getId());
        assertThat(found.getExperienceLevel()).isEqualTo(ExperienceLevel.NEW);
        assertThat(found.getCreatedAt()).isNotNull();
        assertThat(found.getUpdatedAt()).isNotNull();
    }

    @Test
    void checksExistenceByUser() {
        User user = userRepository.save(new User("exists-profile@example.com", "hashed-password", "Moon", null));
        User otherUser = userRepository.save(new User("missing-profile@example.com", "hashed-password", "Choi", null));

        profileRepository.save(new Profile(user, ExperienceLevel.EXPERIENCED));

        assertThat(profileRepository.existsByUser(user)).isTrue();
        assertThat(profileRepository.existsByUser(otherUser)).isFalse();
    }

    @Test
    void enforcesUniqueUserProfile() {
        User user = userRepository.save(new User("duplicate-profile@example.com", "hashed-password", "Moon", null));
        profileRepository.saveAndFlush(new Profile(user, ExperienceLevel.NEW));

        Profile duplicate = new Profile(user, ExperienceLevel.EXPERIENCED);

        assertThatThrownBy(() -> profileRepository.saveAndFlush(duplicate))
                .isInstanceOf(DataIntegrityViolationException.class);
    }
}