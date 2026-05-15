package com.careerchat.backend.auth.controller;

import com.careerchat.backend.auth.dto.LoginRequest;
import com.careerchat.backend.auth.dto.LoginResponse;
import com.careerchat.backend.auth.dto.MeResponse;
import com.careerchat.backend.auth.dto.SignupRequest;
import com.careerchat.backend.auth.dto.SignupResponse;
import com.careerchat.backend.auth.service.LoginService;
import com.careerchat.backend.auth.service.MeService;
import com.careerchat.backend.auth.service.SignupService;
import com.careerchat.backend.global.common.ApiResponse;
import com.careerchat.backend.global.security.AuthenticatedUser;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
public class AuthController {

    private final SignupService signupService;
    private final LoginService loginService;
    private final MeService meService;

    public AuthController(SignupService signupService, LoginService loginService, MeService meService) {
        this.signupService = signupService;
        this.loginService = loginService;
        this.meService = meService;
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

    @GetMapping("/auth/me")
    public ApiResponse<MeResponse> me(@AuthenticationPrincipal AuthenticatedUser authenticatedUser) {
        MeResponse response = meService.getMe(authenticatedUser.userId());

        return ApiResponse.success(response);
    }
}
