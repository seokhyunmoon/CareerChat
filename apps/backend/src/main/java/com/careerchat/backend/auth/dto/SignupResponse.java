package com.careerchat.backend.auth.dto;

public record SignupResponse(
        Long userId,
        String email,
        String name
) {
}
