package com.careerchat.backend.diagnosis.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ChatMessageCreateRequest(
        @NotBlank
        @Size(max = 2000)
        String content
) {
}
