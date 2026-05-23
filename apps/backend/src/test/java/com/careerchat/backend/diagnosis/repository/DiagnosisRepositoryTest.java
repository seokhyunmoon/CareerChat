package com.careerchat.backend.diagnosis.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.repository.ProfileRepository;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.dao.DataIntegrityViolationException;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class DiagnosisRepositoryTest {

    private final UserRepository userRepository;
    private final ProfileRepository profileRepository;
    private final DiagnosisRepository diagnosisRepository;
    private final JDResultRepository jdResultRepository;
    private final ChatMessageRepository chatMessageRepository;

    @Autowired
    DiagnosisRepositoryTest(
            UserRepository userRepository,
            ProfileRepository profileRepository,
            DiagnosisRepository diagnosisRepository,
            JDResultRepository jdResultRepository,
            ChatMessageRepository chatMessageRepository
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.diagnosisRepository = diagnosisRepository;
        this.jdResultRepository = jdResultRepository;
        this.chatMessageRepository = chatMessageRepository;
    }

    @Test
    void savesDiagnosisWithDefaultPendingStatus() {
        Profile profile = createProfile("diagnosis@example.com");

        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));

        assertThat(diagnosis.getId()).isNotNull();
        assertThat(diagnosis.getProfile().getId()).isEqualTo(profile.getId());
        assertThat(diagnosis.getStatus()).isEqualTo(DiagnosisStatus.PENDING);
        assertThat(diagnosis.getCreatedAt()).isNotNull();
        assertThat(diagnosis.getUpdatedAt()).isNotNull();
    }

    @Test
    void findsDiagnosesByProfileInCreatedAtDescOrder() {
        Profile profile = createProfile("diagnosis-list@example.com");
        Diagnosis first = diagnosisRepository.save(new Diagnosis(profile));
        Diagnosis second = diagnosisRepository.save(new Diagnosis(profile));

        List<Diagnosis> diagnoses = diagnosisRepository.findAllByProfileOrderByCreatedAtDescIdDesc(profile);

        assertThat(diagnoses).extracting(Diagnosis::getId)
                .containsExactly(second.getId(), first.getId());
    }

    @Test
    void updatesDiagnosisStatusAndReport() {
        Profile profile = createProfile("diagnosis-complete@example.com");
        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        LocalDateTime completedAt = LocalDateTime.now();

        diagnosis.markProcessing();
        diagnosis.complete("요약", "본문", completedAt);
        diagnosisRepository.flush();

        Diagnosis found = diagnosisRepository.findById(diagnosis.getId()).orElseThrow();

        assertThat(found.getStatus()).isEqualTo(DiagnosisStatus.COMPLETED);
        assertThat(found.getReportSummary()).isEqualTo("요약");
        assertThat(found.getReportContent()).isEqualTo("본문");
        assertThat(found.getCompletedAt()).isEqualTo(completedAt);
    }

    @Test
    void savesDiagnosisAiMetadataAndFailureDetails() {
        Profile profile = createProfile("diagnosis-ai-metadata@example.com");
        Diagnosis diagnosis = new Diagnosis(profile);
        LocalDateTime analysisStartedAt = LocalDateTime.now();
        LocalDateTime failedAt = analysisStartedAt.plusSeconds(30);

        diagnosis.startAnalysis(
                "task-123",
                "{\"experienceLevel\":\"NEW\"}",
                analysisStartedAt
        );
        diagnosis.updateAiMetadata(
                "gpt-4.1-mini",
                "diagnosis-report-v1",
                "{\"durationMs\":30000}"
        );
        diagnosis.fail(
                "AI_TIMEOUT",
                "분석 시간이 초과되었습니다.",
                "REPORT_GENERATION",
                "{\"retryable\":true}",
                failedAt
        );

        Diagnosis saved = diagnosisRepository.saveAndFlush(diagnosis);
        Diagnosis found = diagnosisRepository.findById(saved.getId()).orElseThrow();

        assertThat(found.getStatus()).isEqualTo(DiagnosisStatus.FAILED);
        assertThat(found.getAiTaskId()).isEqualTo("task-123");
        assertThat(found.getProfileSnapshot()).contains("experienceLevel", "NEW");
        assertThat(found.getAnalysisStartedAt()).isEqualTo(analysisStartedAt);
        assertThat(found.getModelName()).isEqualTo("gpt-4.1-mini");
        assertThat(found.getPromptVersion()).isEqualTo("diagnosis-report-v1");
        assertThat(found.getAnalysisMetadata()).contains("durationMs", "30000");
        assertThat(found.getErrorCode()).isEqualTo("AI_TIMEOUT");
        assertThat(found.getErrorMessage()).isEqualTo("분석 시간이 초과되었습니다.");
        assertThat(found.getFailedStep()).isEqualTo("REPORT_GENERATION");
        assertThat(found.getFailedAt()).isEqualTo(failedAt);
        assertThat(found.getErrorDetails()).contains("retryable");
        assertThat(found.getCompletedAt()).isEqualTo(failedAt);
    }

    @Test
    void savesAndFindsJdResultsByDisplayOrder() {
        Profile profile = createProfile("jd-results@example.com");
        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        JDResult second = jdResultRepository.save(new JDResult(
                diagnosis,
                "회사 B",
                "Backend Engineer",
                "공고 B",
                2
        ));
        JDResult first = jdResultRepository.save(new JDResult(
                diagnosis,
                "회사 A",
                "Frontend Engineer",
                "공고 A",
                1
        ));

        first.updateAnalysisResult(
                1,
                new BigDecimal("85.50"),
                "강점",
                "부족",
                "강조",
                "{\"requirements\":[{\"name\":\"Spring\",\"match\":\"HIGH\"}]}"
        );
        jdResultRepository.flush();

        List<JDResult> results = jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis);

        assertThat(results).extracting(JDResult::getId)
                .containsExactly(first.getId(), second.getId());
        assertThat(results.get(0).getFitScore()).isEqualByComparingTo("85.50");
        assertThat(results.get(0).getStrengthsSummary()).isEqualTo("강점");
        assertThat(results.get(0).getGapsSummary()).isEqualTo("부족");
        assertThat(results.get(0).getHighlightPoints()).isEqualTo("강조");
        assertThat(results.get(0).getMatchDetails()).contains("\"requirements\"");
        assertThat(results.get(0).getMatchDetails()).contains("\"Spring\"");
    }

    @Test
    void enforcesUniqueDisplayOrderPerDiagnosis() {
        Profile profile = createProfile("jd-unique-display@example.com");
        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        jdResultRepository.saveAndFlush(new JDResult(
                diagnosis,
                "회사 A",
                "Backend Engineer",
                "공고 A",
                1
        ));

        JDResult duplicate = new JDResult(
                diagnosis,
                "회사 B",
                "Frontend Engineer",
                "공고 B",
                1
        );

        assertThatThrownBy(() -> jdResultRepository.saveAndFlush(duplicate))
                .isInstanceOf(DataIntegrityViolationException.class);
    }

    @Test
    void savesAndFindsChatMessagesByCreatedAt() {
        Profile profile = createProfile("chat-messages@example.com");
        Diagnosis diagnosis = diagnosisRepository.save(new Diagnosis(profile));
        ChatMessage userMessage = chatMessageRepository.save(new ChatMessage(
                diagnosis,
                ChatRole.USER,
                "어떤 공고부터 지원할까?",
                null
        ));
        ChatMessage assistantMessage = chatMessageRepository.save(new ChatMessage(
                diagnosis,
                ChatRole.ASSISTANT,
                "첫 번째 공고를 추천합니다.",
                "{\"jdId\": 1}"
        ));

        List<ChatMessage> messages = chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(diagnosis);

        assertThat(messages).extracting(ChatMessage::getId)
                .containsExactly(userMessage.getId(), assistantMessage.getId());
        assertThat(messages.get(0).getRole()).isEqualTo(ChatRole.USER);
        assertThat(messages.get(1).getRole()).isEqualTo(ChatRole.ASSISTANT);
        assertThat(messages.get(1).getEvidenceData()).isEqualTo("{\"jdId\": 1}");
    }

    private Profile createProfile(String email) {
        User user = userRepository.save(new User(email, "hashed-password", "문석현", null));
        return profileRepository.save(new Profile(user, ExperienceLevel.NEW));
    }
}
