package com.careerchat.backend.auth.dto;

public record MeResponse(
        Long userId,
        String email,
        String name
) {
}
