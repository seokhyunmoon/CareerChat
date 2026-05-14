package com.careerchat.backend.auth.service;

import com.careerchat.backend.auth.dto.SignupRequest;
import com.careerchat.backend.auth.dto.SignupResponse;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class SignupService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public SignupService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public SignupResponse signup(SignupRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new BusinessException(ErrorCode.DUPLICATE_RESOURCE, "Email already exists.");
        }

        String passwordHash = passwordEncoder.encode(request.password());
        User user = new User(request.email(), passwordHash, request.name(), request.telephone());
        User savedUser = userRepository.save(user);

        return new SignupResponse(savedUser.getId(), savedUser.getEmail(), savedUser.getName());
    }
}
