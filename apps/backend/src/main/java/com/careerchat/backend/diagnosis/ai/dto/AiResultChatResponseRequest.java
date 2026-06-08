package com.careerchat.backend.diagnosis.ai.dto;

import com.careerchat.backend.diagnosis.domain.ChatRole;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

public record AiResultChatResponseRequest(
        Long diagnosisId,
        String userMessage,
        String reportSummary,
        String reportContent,
        List<JobResult> jobResults,
        List<PreviousMessage> previousMessages
) {

    public record JobResult(
            Long jdId,
            Integer rankOrder,
            String companyName,
            String position,
            BigDecimal fitScore,
            String strengthsSummary,
            String gapsSummary,
            List<String> highlightPoints,
            List<Map<String, Object>> matchDetails
    ) {
    }

    public record PreviousMessage(
            ChatRole role,
            String content
    ) {
    }
}
