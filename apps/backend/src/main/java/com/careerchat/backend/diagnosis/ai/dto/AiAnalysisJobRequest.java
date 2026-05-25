package com.careerchat.backend.diagnosis.ai.dto;

import java.util.List;

public record AiAnalysisJobRequest(
        Long diagnosisId,
        CallbackTarget callback,
        AiProfileSnapshot profileSnapshot,
        List<JobPosting> jobs
) {

    public record CallbackTarget(
            String completeUrl,
            String failUrl
    ) {
    }

    public record JobPosting(
            Long jdId,
            Integer displayOrder,
            String companyName,
            String position,
            String content
    ) {
    }
}
