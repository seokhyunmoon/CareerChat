package com.careerchat.backend.auth.dto;

public record LoginResponse(
        Long userId,
        String email,
        String name,
        String accessToken
) {
}
