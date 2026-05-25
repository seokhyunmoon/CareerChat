package com.careerchat.backend.diagnosis.ai.service;

import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClient;
import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClientException;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.diagnosis.ai.dto.AiProfileSnapshot;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class AiAnalysisJobStarter {

    private static final String ENQUEUE_FAILED_CODE = "AI_JOB_ENQUEUE_FAILED";
    private static final String ENQUEUE_FAILED_STEP = "JOB_ENQUEUE";
    private static final String ENQUEUE_FAILED_MESSAGE = "AI analysis request failed.";

    private final ProfileSnapshotFactory profileSnapshotFactory;
    private final AiAnalysisJobRequestFactory requestFactory;
    private final AiAnalysisClient aiAnalysisClient;
    private final ObjectMapper objectMapper;

    public AiAnalysisJobStarter(
            ProfileSnapshotFactory profileSnapshotFactory,
            AiAnalysisJobRequestFactory requestFactory,
            AiAnalysisClient aiAnalysisClient,
            ObjectMapper objectMapper
    ) {
        this.profileSnapshotFactory = profileSnapshotFactory;
        this.requestFactory = requestFactory;
        this.aiAnalysisClient = aiAnalysisClient;
        this.objectMapper = objectMapper;
    }

    public void start(Diagnosis diagnosis, List<JDResult> jdResults) {
        AiProfileSnapshot profileSnapshot = profileSnapshotFactory.create(diagnosis.getProfile());

        try {
            String profileSnapshotJson = writeJson(profileSnapshot);
            AiAnalysisJobRequest request = requestFactory.create(diagnosis, profileSnapshot, jdResults);
            AiAnalysisJobCreateResponse response = aiAnalysisClient.createAnalysisJob(request);
            diagnosis.startAnalysis(
                    response.taskId(),
                    profileSnapshotJson,
                    LocalDateTime.now()
            );
        } catch (AiAnalysisClientException exception) {
            diagnosis.fail(
                    ENQUEUE_FAILED_CODE,
                    ENQUEUE_FAILED_MESSAGE,
                    ENQUEUE_FAILED_STEP,
                    writeErrorDetails(exception),
                    LocalDateTime.now()
            );
        }
    }

    private String writeJson(AiProfileSnapshot profileSnapshot) {
        try {
            return objectMapper.writeValueAsString(profileSnapshot);
        } catch (JsonProcessingException exception) {
            throw new AiAnalysisClientException("Failed to serialize profile snapshot.", exception);
        }
    }

    private String writeErrorDetails(AiAnalysisClientException exception) {
        try {
            return objectMapper.writeValueAsString(Map.of(
                    "message", exception.getMessage(),
                    "retryable", true
            ));
        } catch (JsonProcessingException jsonException) {
            return null;
        }
    }
}
