package com.careerchat.backend.diagnosis.ai.dto;

public record AiAnalysisJobCreateResponse(
        Long diagnosisId,
        String taskId,
        String status
) {
}
