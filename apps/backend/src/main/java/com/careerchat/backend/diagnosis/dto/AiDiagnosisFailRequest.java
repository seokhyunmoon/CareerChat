package com.careerchat.backend.diagnosis.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;

public record AiDiagnosisFailRequest(
        @NotBlank
        String taskId,

        @Size(max = 100)
        String errorCode,

        @NotBlank
        String errorMessage,

        @Size(max = 100)
        String failedStep,

        @NotNull
        LocalDateTime failedAt,

        String errorDetails
) {
}
