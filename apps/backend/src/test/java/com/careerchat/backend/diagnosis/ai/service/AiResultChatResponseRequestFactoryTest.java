package com.careerchat.backend.diagnosis.ai.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class AiResultChatResponseRequestFactoryTest {

    private AiResultChatResponseRequestFactory factory;

    @BeforeEach
    void setUp() {
        factory = new AiResultChatResponseRequestFactory(new ObjectMapper());
    }

    @Test
    void createMapsDiagnosisResultContextToAiRequest() {
        Diagnosis diagnosis = createCompletedDiagnosis();
        JDResult jdResult = createAnalyzedJdResult(diagnosis);
        ChatMessage userMessage = createMessage(300L, diagnosis, ChatRole.USER, "강점을 알려줘");
        List<ChatMessage> previousMessages = createPreviousMessages(diagnosis, 21);

        AiResultChatResponseRequest request = factory.create(
                diagnosis,
                List.of(jdResult),
                userMessage,
                previousMessages
        );

        assertThat(request.diagnosisId()).isEqualTo(100L);
        assertThat(request.userMessage()).isEqualTo("강점을 알려줘");
        assertThat(request.reportSummary()).isEqualTo("지원 우선순위 요약");
        assertThat(request.reportContent()).isEqualTo("상세 리포트 본문");
        assertThat(request.jobResults()).hasSize(1);
        assertThat(request.jobResults().getFirst().jdId()).isEqualTo(200L);
        assertThat(request.jobResults().getFirst().rankOrder()).isEqualTo(1);
        assertThat(request.jobResults().getFirst().companyName()).isEqualTo("토스");
        assertThat(request.jobResults().getFirst().fitScore()).isEqualByComparingTo("28.50");
        assertThat(request.jobResults().getFirst().highlightPoints())
                .containsExactly("RAG 시스템 개발", "LLM reranking");
        assertThat(request.jobResults().getFirst().matchDetails())
                .hasSize(1)
                .first()
                .extracting(match -> match.get("name"), match -> match.get("match"))
                .containsExactly("RAG", "HIGH");
        assertThat(request.previousMessages()).hasSize(20);
        assertThat(request.previousMessages().getFirst().content()).isEqualTo("이전 메시지 2");
        assertThat(request.previousMessages().getLast().content()).isEqualTo("이전 메시지 21");
    }

    @Test
    void createThrowsDiagnosisNotCompletedWhenResultContextIsMissing() {
        User user = new User("owner@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", 100L);
        ChatMessage userMessage = createMessage(300L, diagnosis, ChatRole.USER, "질문");

        assertThatThrownBy(() -> factory.create(diagnosis, List.of(), userMessage, List.of()))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis result is not ready for chat.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.DIAGNOSIS_NOT_COMPLETED);
    }

    private Diagnosis createCompletedDiagnosis() {
        User user = new User("owner@example.com", "hashed-password", "문석현", null);
        ReflectionTestUtils.setField(user, "id", 1L);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ReflectionTestUtils.setField(profile, "id", 10L);
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", 100L);
        diagnosis.complete("지원 우선순위 요약", "상세 리포트 본문", LocalDateTime.of(2026, 6, 8, 10, 0));
        return diagnosis;
    }

    private JDResult createAnalyzedJdResult(Diagnosis diagnosis) {
        JDResult jdResult = new JDResult(diagnosis, "토스", "AI Engineer", "채용공고 본문", 1);
        ReflectionTestUtils.setField(jdResult, "id", 200L);
        jdResult.updateAnalysisResult(
                1,
                new BigDecimal("28.50"),
                "RAG 구성 요소 설계 경험",
                "다중 팀 협업 경험",
                "[\"RAG 시스템 개발\",\"LLM reranking\"]",
                "{\"requirements\":[{\"name\":\"RAG\",\"match\":\"HIGH\"}]}"
        );
        return jdResult;
    }

    private List<ChatMessage> createPreviousMessages(Diagnosis diagnosis, int count) {
        return java.util.stream.IntStream.rangeClosed(1, count)
                .mapToObj(index -> createMessage(
                        (long) index,
                        diagnosis,
                        index % 2 == 0 ? ChatRole.ASSISTANT : ChatRole.USER,
                        "이전 메시지 " + index
                ))
                .toList();
    }

    private ChatMessage createMessage(Long id, Diagnosis diagnosis, ChatRole role, String content) {
        ChatMessage chatMessage = new ChatMessage(diagnosis, role, content, null);
        ReflectionTestUtils.setField(chatMessage, "id", id);
        ReflectionTestUtils.setField(chatMessage, "createdAt", LocalDateTime.of(2026, 6, 8, 10, id.intValue() % 60));
        return chatMessage;
    }
}
