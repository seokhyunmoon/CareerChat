package com.careerchat.backend.diagnosis.ai.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClient;
import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClientException;
import com.careerchat.backend.diagnosis.ai.config.AiBackendProperties;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobCreateResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.diagnosis.ai.dto.AiProfileSnapshot;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.test.util.ReflectionTestUtils;

class AiAnalysisJobStarterTest {

    private ProfileSnapshotFactory profileSnapshotFactory;
    private AiAnalysisClient aiAnalysisClient;
    private AiAnalysisJobStarter starter;

    @BeforeEach
    void setUp() {
        profileSnapshotFactory = mock(ProfileSnapshotFactory.class);
        aiAnalysisClient = mock(AiAnalysisClient.class);
        AiAnalysisJobRequestFactory requestFactory = new AiAnalysisJobRequestFactory(new AiBackendProperties());
        ObjectMapper objectMapper = new ObjectMapper().findAndRegisterModules();
        starter = new AiAnalysisJobStarter(
                profileSnapshotFactory,
                requestFactory,
                aiAnalysisClient,
                objectMapper
        );
    }

    @Test
    void startEnqueuesAnalysisJobAndStoresTaskIdAndSnapshot() {
        Diagnosis diagnosis = createDiagnosis();
        JDResult jdResult = createJdResult(diagnosis);
        AiProfileSnapshot snapshot = createSnapshot();

        when(profileSnapshotFactory.create(diagnosis.getProfile())).thenReturn(snapshot);
        when(aiAnalysisClient.createAnalysisJob(any()))
                .thenReturn(new AiAnalysisJobCreateResponse(100L, "task-123", "QUEUED"));

        starter.start(diagnosis, List.of(jdResult));

        ArgumentCaptor<AiAnalysisJobRequest> requestCaptor = ArgumentCaptor.forClass(AiAnalysisJobRequest.class);
        verify(aiAnalysisClient).createAnalysisJob(requestCaptor.capture());
        AiAnalysisJobRequest request = requestCaptor.getValue();

        assertThat(request.diagnosisId()).isEqualTo(100L);
        assertThat(request.profileSnapshot()).isSameAs(snapshot);
        assertThat(request.jobs()).hasSize(1);
        assertThat(request.jobs().getFirst().jdId()).isEqualTo(200L);
        assertThat(request.callback().completeUrl()).endsWith("/internal/ai/diagnoses/100/complete");
        assertThat(request.callback().failUrl()).endsWith("/internal/ai/diagnoses/100/fail");
        assertThat(diagnosis.getStatus()).isEqualTo(DiagnosisStatus.PROCESSING);
        assertThat(diagnosis.getAiTaskId()).isEqualTo("task-123");
        assertThat(diagnosis.getProfileSnapshot()).contains("\"snapshotVersion\":1", "\"profileId\":10");
        assertThat(diagnosis.getAnalysisStartedAt()).isNotNull();
    }

    @Test
    void startMarksDiagnosisFailedWhenAiBackendRequestFails() {
        Diagnosis diagnosis = createDiagnosis();
        JDResult jdResult = createJdResult(diagnosis);

        when(profileSnapshotFactory.create(diagnosis.getProfile())).thenReturn(createSnapshot());
        when(aiAnalysisClient.createAnalysisJob(any()))
                .thenThrow(new AiAnalysisClientException("timeout"));

        starter.start(diagnosis, List.of(jdResult));

        assertThat(diagnosis.getStatus()).isEqualTo(DiagnosisStatus.FAILED);
        assertThat(diagnosis.getErrorCode()).isEqualTo("AI_JOB_ENQUEUE_FAILED");
        assertThat(diagnosis.getErrorMessage()).isEqualTo("AI analysis request failed.");
        assertThat(diagnosis.getFailedStep()).isEqualTo("JOB_ENQUEUE");
        assertThat(diagnosis.getErrorDetails()).contains("timeout", "retryable");
        assertThat(diagnosis.getFailedAt()).isNotNull();
    }

    private Diagnosis createDiagnosis() {
        User user = new User("user@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ReflectionTestUtils.setField(profile, "id", 10L);
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", 100L);
        return diagnosis;
    }

    private JDResult createJdResult(Diagnosis diagnosis) {
        JDResult jdResult = new JDResult(diagnosis, "회사 A", "Backend Engineer", "공고 내용", 1);
        ReflectionTestUtils.setField(jdResult, "id", 200L);
        return jdResult;
    }

    private AiProfileSnapshot createSnapshot() {
        return new AiProfileSnapshot(
                1,
                new AiProfileSnapshot.SnapshotProfile(10L, "NEW"),
                List.of(),
                List.of(),
                List.of(),
                List.of()
        );
    }
}
