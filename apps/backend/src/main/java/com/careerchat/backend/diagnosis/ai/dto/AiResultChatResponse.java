package com.careerchat.backend.diagnosis.ai.dto;

import java.util.List;

public record AiResultChatResponse(
        String content,
        EvidenceData evidenceData,
        String providerName,
        String modelName,
        String promptKey,
        String promptVersion
) {

    public record EvidenceData(
            List<Long> referencedJobIds,
            List<String> reasonCodes,
            List<String> usedFields
    ) {
    }
}
