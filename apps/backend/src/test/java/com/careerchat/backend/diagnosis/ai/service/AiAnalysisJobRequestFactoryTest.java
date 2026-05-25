package com.careerchat.backend.diagnosis.ai.service;

import static org.assertj.core.api.Assertions.assertThat;

import com.careerchat.backend.diagnosis.ai.config.AiBackendProperties;
import com.careerchat.backend.diagnosis.ai.dto.AiAnalysisJobRequest;
import com.careerchat.backend.diagnosis.ai.dto.AiProfileSnapshot;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import java.net.URI;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class AiAnalysisJobRequestFactoryTest {

    @Test
    void createBuildsAnalysisJobRequestWithCallbackUrlsAndJobs() {
        AiBackendProperties properties = new AiBackendProperties();
        properties.setCallbackBaseUrl(URI.create("https://spring.example.com"));
        AiAnalysisJobRequestFactory factory = new AiAnalysisJobRequestFactory(properties);

        User user = new User("user@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", 100L);

        JDResult jdResult = new JDResult(diagnosis, "회사 A", "Backend Engineer", "공고 내용", 1);
        ReflectionTestUtils.setField(jdResult, "id", 200L);

        AiProfileSnapshot snapshot = new AiProfileSnapshot(
                1,
                new AiProfileSnapshot.SnapshotProfile(10L, "NEW"),
                List.of(),
                List.of(),
                List.of(),
                List.of()
        );

        AiAnalysisJobRequest request = factory.create(diagnosis, snapshot, List.of(jdResult));

        assertThat(request.diagnosisId()).isEqualTo(100L);
        assertThat(request.callback().completeUrl())
                .isEqualTo("https://spring.example.com/internal/ai/diagnoses/100/complete");
        assertThat(request.callback().failUrl())
                .isEqualTo("https://spring.example.com/internal/ai/diagnoses/100/fail");
        assertThat(request.profileSnapshot()).isSameAs(snapshot);
        assertThat(request.jobs()).hasSize(1);
        assertThat(request.jobs().getFirst())
                .extracting(
                        AiAnalysisJobRequest.JobPosting::jdId,
                        AiAnalysisJobRequest.JobPosting::displayOrder,
                        AiAnalysisJobRequest.JobPosting::companyName,
                        AiAnalysisJobRequest.JobPosting::position,
                        AiAnalysisJobRequest.JobPosting::content
                )
                .containsExactly(200L, 1, "회사 A", "Backend Engineer", "공고 내용");
    }
}
