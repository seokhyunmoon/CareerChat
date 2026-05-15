package com.careerchat.backend.auth.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.careerchat.backend.auth.dto.MeResponse;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MeServiceTest {

    private UserRepository userRepository;
    private MeService meService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        meService = new MeService(userRepository);
    }

    @Test
    void getMeReturnsCurrentUserInfo() {
        User user = new User("user@example.com", "hashed-password", "Moon", "010-1234-5678");
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        MeResponse response = meService.getMe(1L);

        assertThat(response.email()).isEqualTo("user@example.com");
        assertThat(response.name()).isEqualTo("Moon");
    }

    @Test
    void getMeThrowsUnauthorizedWhenUserDoesNotExist() {
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> meService.getMe(1L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Authentication is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);
    }
}