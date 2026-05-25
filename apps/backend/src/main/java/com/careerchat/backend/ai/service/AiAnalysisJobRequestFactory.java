package com.careerchat.backend.ai.service;

import com.careerchat.backend.ai.config.AiBackendProperties;
import com.careerchat.backend.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.ai.dto.AiProfileSnapshot;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import java.util.List;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

@Component
public class AiAnalysisJobRequestFactory {

    private final AiBackendProperties properties;

    public AiAnalysisJobRequestFactory(AiBackendProperties properties) {
        this.properties = properties;
    }

    public AiAnalysisJobRequest create(
            Diagnosis diagnosis,
            AiProfileSnapshot profileSnapshot,
            List<JDResult> jdResults
    ) {
        Long diagnosisId = diagnosis.getId();

        return new AiAnalysisJobRequest(
                diagnosisId,
                new AiAnalysisJobRequest.CallbackTarget(
                        buildCallbackUrl(diagnosisId, "complete"),
                        buildCallbackUrl(diagnosisId, "fail")
                ),
                profileSnapshot,
                jdResults.stream()
                        .map(this::toJobPosting)
                        .toList()
        );
    }

    private AiAnalysisJobRequest.JobPosting toJobPosting(JDResult jdResult) {
        return new AiAnalysisJobRequest.JobPosting(
                jdResult.getId(),
                jdResult.getDisplayOrder(),
                jdResult.getCompanyName(),
                jdResult.getPosition(),
                jdResult.getContent()
        );
    }

    private String buildCallbackUrl(Long diagnosisId, String statusPath) {
        return UriComponentsBuilder.fromUri(properties.getCallbackBaseUrl())
                .pathSegment("internal", "ai", "diagnoses", "{diagnosisId}", "{statusPath}")
                .buildAndExpand(diagnosisId, statusPath)
                .toUriString();
    }
}
