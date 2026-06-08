package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.fasterxml.jackson.annotation.JsonRawValue;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record DiagnosisResultResponse(
        Long diagnosisId,
        DiagnosisStatus status,
        LocalDateTime createdAt,
        LocalDateTime analysisStartedAt,
        LocalDateTime completedAt,
        LocalDateTime failedAt,
        String reportSummary,
        String reportContent,
        String errorCode,
        String errorMessage,
        List<JobResultResponse> jobs
) {

    public static DiagnosisResultResponse of(Diagnosis diagnosis, List<JDResult> jdResults) {
        return new DiagnosisResultResponse(
                diagnosis.getId(),
                diagnosis.getStatus(),
                diagnosis.getCreatedAt(),
                diagnosis.getAnalysisStartedAt(),
                diagnosis.getCompletedAt(),
                diagnosis.getFailedAt(),
                diagnosis.getReportSummary(),
                diagnosis.getReportContent(),
                diagnosis.getErrorCode(),
                diagnosis.getErrorMessage(),
                jdResults.stream()
                        .map(JobResultResponse::from)
                        .toList()
        );
    }

    public record JobResultResponse(
            Long jdId,
            Integer displayOrder,
            Integer rankOrder,
            String companyName,
            String position,
            BigDecimal fitScore,
            String strengthsSummary,
            String gapsSummary,
            String highlightPoints,
            @JsonRawValue String strengths,
            @JsonRawValue String relatedExperiences,
            @JsonRawValue String gaps,
            @JsonRawValue String resumeHighlights,
            @JsonRawValue String strategyAdvice,
            @JsonRawValue String matchDetails
    ) {

        @JsonRawValue
        public String strengths() {
            return strengths;
        }

        @JsonRawValue
        public String relatedExperiences() {
            return relatedExperiences;
        }

        @JsonRawValue
        public String gaps() {
            return gaps;
        }

        @JsonRawValue
        public String resumeHighlights() {
            return resumeHighlights;
        }

        @JsonRawValue
        public String strategyAdvice() {
            return strategyAdvice;
        }

        @JsonRawValue
        public String matchDetails() {
            return matchDetails;
        }

        static JobResultResponse from(JDResult jdResult) {
            return new JobResultResponse(
                    jdResult.getId(),
                    jdResult.getDisplayOrder(),
                    jdResult.getRankOrder(),
                    jdResult.getCompanyName(),
                    jdResult.getPosition(),
                    jdResult.getFitScore(),
                    jdResult.getStrengthsSummary(),
                    jdResult.getGapsSummary(),
                    jdResult.getHighlightPoints(),
                    jdResult.getStrengths(),
                    jdResult.getRelatedExperiences(),
                    jdResult.getGaps(),
                    jdResult.getResumeHighlights(),
                    jdResult.getStrategyAdvice(),
                    jdResult.getMatchDetails()
            );
        }
    }
}
