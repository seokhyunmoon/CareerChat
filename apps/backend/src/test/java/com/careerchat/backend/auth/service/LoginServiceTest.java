package com.careerchat.backend.auth.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.careerchat.backend.auth.dto.LoginRequest;
import com.careerchat.backend.auth.dto.LoginResponse;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

class LoginServiceTest {

    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;
    private LoginService loginService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        passwordEncoder = new BCryptPasswordEncoder();
        loginService = new LoginService(userRepository, passwordEncoder);
    }

    @Test
    void loginReturnsUserInfoWhenCredentialsAreValid() {
        String passwordHash = passwordEncoder.encode("password123");
        User user = new User("user@example.com", passwordHash, "Moon", null);

        LoginRequest request = new LoginRequest("user@example.com", "password123");
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.of(user));

        LoginResponse response = loginService.login(request);

        assertThat(response.email()).isEqualTo("user@example.com");
        assertThat(response.name()).isEqualTo("Moon");
    }

    @Test
    void loginThrowsUnauthorizedWhenEmailDoesNotExist() {
        LoginRequest request = new LoginRequest("user@example.com", "password123");
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> loginService.login(request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Invalid email or password.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);
    }

    @Test
    void loginThrowsUnauthorizedWhenPasswordDoesNotMatch() {
        String passwordHash = passwordEncoder.encode("password123");
        User user = new User("user@example.com", passwordHash, "Moon", null);

        LoginRequest request = new LoginRequest("user@example.com", "wrongpassword");
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.of(user));

        assertThatThrownBy(() -> loginService.login(request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Invalid email or password.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);
    }
}