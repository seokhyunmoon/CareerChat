package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;

public record DiagnosisHistoryResponse(
        List<DiagnosisSummaryResponse> diagnoses
) {

    public record DiagnosisSummaryResponse(
            Long diagnosisId,
            DiagnosisStatus status,
            LocalDateTime createdAt,
            LocalDateTime analysisStartedAt,
            LocalDateTime completedAt,
            LocalDateTime failedAt,
            List<String> companies,
            String jobsSummary,
            Integer jobCount,
            String topCompanyName,
            String topPosition,
            BigDecimal topFitScore,
            String errorMessage
    ) {

        public static DiagnosisSummaryResponse of(Diagnosis diagnosis, List<JDResult> jdResults) {
            JDResult topResult = findTopResult(jdResults);

            return new DiagnosisSummaryResponse(
                    diagnosis.getId(),
                    diagnosis.getStatus(),
                    diagnosis.getCreatedAt(),
                    diagnosis.getAnalysisStartedAt(),
                    diagnosis.getCompletedAt(),
                    diagnosis.getFailedAt(),
                    jdResults.stream()
                            .map(JDResult::getCompanyName)
                            .toList(),
                    createJobsSummary(jdResults),
                    jdResults.size(),
                    topResult == null ? null : topResult.getCompanyName(),
                    topResult == null ? null : topResult.getPosition(),
                    topResult == null ? null : topResult.getFitScore(),
                    diagnosis.getErrorMessage()
            );
        }

        private static JDResult findTopResult(List<JDResult> jdResults) {
            return jdResults.stream()
                    .filter(jdResult -> jdResult.getRankOrder() != null)
                    .min(Comparator.comparing(JDResult::getRankOrder))
                    .orElseGet(() -> jdResults.isEmpty() ? null : jdResults.getFirst());
        }

        private static String createJobsSummary(List<JDResult> jdResults) {
            return String.join(
                    " · ",
                    jdResults.stream()
                            .map(JDResult::getPosition)
                            .filter(position -> position != null && !position.isBlank())
                            .toList()
            );
        }
    }
}
