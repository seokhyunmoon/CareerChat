package com.careerchat.backend.auth.controller;

import com.careerchat.backend.auth.dto.SignupRequest;
import com.careerchat.backend.auth.dto.SignupResponse;
import com.careerchat.backend.auth.service.SignupService;
import com.careerchat.backend.global.common.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AuthController {

    private final SignupService signupService;

    public AuthController(SignupService signupService) {
        this.signupService = signupService;
    }

    @PostMapping("/auth/signup")
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<SignupResponse> signup(@Valid @RequestBody SignupRequest request) {
        SignupResponse response = signupService.signup(request);

        return ApiResponse.success(response);
    }
}
