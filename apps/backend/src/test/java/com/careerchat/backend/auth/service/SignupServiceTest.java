package com.careerchat.backend.auth.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.auth.dto.SignupRequest;
import com.careerchat.backend.auth.dto.SignupResponse;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

class SignupServiceTest {

    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;
    private SignupService signupService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        passwordEncoder = new BCryptPasswordEncoder();
        signupService = new SignupService(userRepository, passwordEncoder);
    }

    @Test
    void signupSavesUserWithEncodedPassword() {
        SignupRequest request = new SignupRequest("Moon", "user@example.com", "password123", "010-1234-5678");
        when(userRepository.existsByEmail("user@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> invocation.getArgument(0));

        SignupResponse response = signupService.signup(request);

        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        verify(userRepository).save(userCaptor.capture());

        User savedUser = userCaptor.getValue();
        assertThat(savedUser.getEmail()).isEqualTo("user@example.com");
        assertThat(savedUser.getName()).isEqualTo("Moon");
        assertThat(savedUser.getPasswordHash()).isNotEqualTo("password123");
        assertThat(savedUser.getTelephone()).isEqualTo("010-1234-5678");
        assertThat(passwordEncoder.matches("password123", savedUser.getPasswordHash())).isTrue();

        assertThat(response.email()).isEqualTo("user@example.com");
        assertThat(response.name()).isEqualTo("Moon");
    }

    @Test
    void signupThrowsExceptionWhenEmailAlreadyExists() {
        SignupRequest request = new SignupRequest("Moon", "user@example.com", "password123", null);
        when(userRepository.existsByEmail("user@example.com")).thenReturn(true);

        assertThatThrownBy(() -> signupService.signup(request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Email already exists.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.DUPLICATE_RESOURCE);
    }
}
