package com.careerchat.backend.auth.controller;

import com.careerchat.backend.auth.dto.LoginRequest;
import com.careerchat.backend.auth.dto.LoginResponse;
import com.careerchat.backend.auth.dto.SignupRequest;
import com.careerchat.backend.auth.dto.SignupResponse;
import com.careerchat.backend.auth.service.LoginService;
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
    private final LoginService loginService;

    public AuthController(SignupService signupService, LoginService loginService) {
        this.signupService = signupService;
        this.loginService = loginService;
    }

    @PostMapping("/auth/signup")
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<SignupResponse> signup(@Valid @RequestBody SignupRequest request) {
        SignupResponse response = signupService.signup(request);

        return ApiResponse.success(response);
    }

    @PostMapping("/auth/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = loginService.login(request);

        return ApiResponse.success(response);
    }
}
