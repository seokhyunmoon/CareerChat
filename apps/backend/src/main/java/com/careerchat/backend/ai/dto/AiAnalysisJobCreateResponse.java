package com.careerchat.backend.ai.dto;

public record AiAnalysisJobCreateResponse(
        Long diagnosisId,
        String taskId,
        String status
) {
}
