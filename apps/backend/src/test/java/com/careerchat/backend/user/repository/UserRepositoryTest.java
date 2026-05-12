package com.careerchat.backend.user.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.careerchat.backend.user.domain.User;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.dao.DataIntegrityViolationException;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class UserRepositoryTest {

	private final UserRepository userRepository;

	@Autowired
	UserRepositoryTest(UserRepository userRepository) {
		this.userRepository = userRepository;
	}

	@Test
	void savesAndFindsByEmail() {
		User user = new User("user@example.com", "hashed-password", "Moon", "010-1234-5678");
		userRepository.save(user);

		User found = userRepository.findByEmail("user@example.com").orElseThrow();

		assertThat(found.getId()).isNotNull();
		assertThat(found.getEmail()).isEqualTo("user@example.com");
		assertThat(found.getPasswordHash()).isEqualTo("hashed-password");
		assertThat(found.getName()).isEqualTo("Moon");
		assertThat(found.getTelephone()).isEqualTo("010-1234-5678");
		assertThat(found.getCreatedAt()).isNotNull();
		assertThat(found.getUpdatedAt()).isNotNull();
	}

	@Test
	void checksExistenceByEmail() {
		userRepository.save(new User("exists@example.com", "hashed-password", "Moon", null));

		assertThat(userRepository.existsByEmail("exists@example.com")).isTrue();
		assertThat(userRepository.existsByEmail("missing@example.com")).isFalse();
	}

	@Test
	void enforcesUniqueEmail() {
		userRepository.saveAndFlush(new User("duplicate@example.com", "hashed-password", "Moon", null));

		User duplicate = new User("duplicate@example.com", "other-hashed-password", "Choi", null);

		assertThatThrownBy(() -> userRepository.saveAndFlush(duplicate))
			.isInstanceOf(DataIntegrityViolationException.class);
	}
}
