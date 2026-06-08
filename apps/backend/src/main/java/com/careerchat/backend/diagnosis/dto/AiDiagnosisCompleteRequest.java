package com.careerchat.backend.diagnosis.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record AiDiagnosisCompleteRequest(
        @NotBlank
        String taskId,

        @NotBlank
        String reportSummary,

        @NotBlank
        String reportContent,

        @NotNull
        LocalDateTime completedAt,

        @Size(max = 100)
        String modelName,

        @Size(max = 100)
        String promptVersion,

        String analysisMetadata,

        @NotNull
        @Size(min = 1)
        List<@Valid JobResultRequest> jobs
) {

    public record JobResultRequest(
            @NotNull
            Long jdId,

            @NotNull
            Integer rankOrder,

            @NotNull
            @DecimalMin("0.00")
            @DecimalMax("100.00")
            BigDecimal fitScore,

            String strengthsSummary,

            String gapsSummary,

            String highlightPoints,

            String strengths,

            String relatedExperiences,

            String gaps,

            String resumeHighlights,

            String strategyAdvice,

            String matchDetails
    ) {
    }
}
