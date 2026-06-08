package com.careerchat.backend.diagnosis.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.service.AiResultChatResponseRequester;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateRequest;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessageResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessagesResponse;
import com.careerchat.backend.diagnosis.repository.ChatMessageRepository;
import com.careerchat.backend.diagnosis.repository.DiagnosisRepository;
import com.careerchat.backend.diagnosis.repository.JDResultRepository;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class DiagnosisChatMessageServiceTest {

    private UserRepository userRepository;
    private DiagnosisRepository diagnosisRepository;
    private JDResultRepository jdResultRepository;
    private ChatMessageRepository chatMessageRepository;
    private AiResultChatResponseRequester aiResultChatResponseRequester;
    private DiagnosisChatMessageService diagnosisChatMessageService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        diagnosisRepository = mock(DiagnosisRepository.class);
        jdResultRepository = mock(JDResultRepository.class);
        chatMessageRepository = mock(ChatMessageRepository.class);
        aiResultChatResponseRequester = mock(AiResultChatResponseRequester.class);
        diagnosisChatMessageService = new DiagnosisChatMessageService(
                userRepository,
                diagnosisRepository,
                jdResultRepository,
                chatMessageRepository,
                aiResultChatResponseRequester,
                new ObjectMapper()
        );
    }

    @Test
    void getMessagesReturnsMessagesInRepositoryOrder() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        ChatMessage userMessage = createMessage(1000L, diagnosis, ChatRole.USER, "질문", null);
        ChatMessage assistantMessage = createMessage(
                1001L,
                diagnosis,
                ChatRole.ASSISTANT,
                "답변",
                "{\"jdId\":1}"
        );

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));
        when(chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(diagnosis))
                .thenReturn(List.of(userMessage, assistantMessage));

        ChatMessagesResponse response = diagnosisChatMessageService.getMessages(1L, 100L);

        assertThat(response.messages()).hasSize(2);
        assertThat(response.messages()).extracting(ChatMessageResponse::messageId)
                .containsExactly(1000L, 1001L);
        assertThat(response.messages().getFirst().role()).isEqualTo(ChatRole.USER);
        assertThat(response.messages().get(1).role()).isEqualTo(ChatRole.ASSISTANT);
        assertThat(response.messages().get(1).evidenceData()).isEqualTo("{\"jdId\":1}");
    }

    @Test
    void getMessagesThrowsResourceNotFoundWhenDiagnosisDoesNotExist() {
        User user = createUser(1L, "missing-diagnosis@example.com");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisChatMessageService.getMessages(1L, 100L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis not found.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.RESOURCE_NOT_FOUND);

        verify(chatMessageRepository, never()).findAllByDiagnosisOrderByCreatedAtAscIdAsc(any());
    }

    @Test
    void getMessagesThrowsForbiddenWhenDiagnosisBelongsToOtherUser() {
        User requester = createUser(1L, "requester@example.com");
        User owner = createUser(2L, "owner@example.com");
        Profile profile = createProfile(10L, owner);
        Diagnosis diagnosis = createDiagnosis(100L, profile);

        when(userRepository.findById(1L)).thenReturn(Optional.of(requester));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));

        assertThatThrownBy(() -> diagnosisChatMessageService.getMessages(1L, 100L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Cannot access this diagnosis.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.FORBIDDEN);

        verify(chatMessageRepository, never()).findAllByDiagnosisOrderByCreatedAtAscIdAsc(any());
    }

    @Test
    void createUserMessageSavesUserAndAssistantMessagesForCompletedDiagnosis() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        diagnosis.complete("요약", "본문", LocalDateTime.of(2026, 6, 8, 10, 0));
        JDResult jdResult = createJdResult(200L, diagnosis);
        ChatMessage previousMessage = createMessage(
                999L,
                diagnosis,
                ChatRole.ASSISTANT,
                "이전 답변",
                "{\"referencedJobIds\":[200]}"
        );
        ChatMessageCreateRequest request = new ChatMessageCreateRequest("어떤 공고부터 지원할까?");
        AiResultChatResponse aiResponse = new AiResultChatResponse(
                "토스 공고를 먼저 추천합니다.",
                new AiResultChatResponse.EvidenceData(
                        List.of(200L),
                        List.of("FIT_SCORE"),
                        List.of("reportSummary", "jobResults")
                ),
                "groq",
                "llama-3.1",
                "result_chat_response",
                "v1"
        );

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));
        when(chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(diagnosis))
                .thenReturn(List.of(previousMessage));
        when(jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis))
                .thenReturn(List.of(jdResult));
        when(chatMessageRepository.save(any(ChatMessage.class))).thenAnswer(invocation -> {
            ChatMessage chatMessage = invocation.getArgument(0);
            long messageId = chatMessage.getRole() == ChatRole.USER ? 1000L : 1001L;
            ReflectionTestUtils.setField(chatMessage, "id", messageId);
            ReflectionTestUtils.setField(chatMessage, "createdAt", LocalDateTime.of(2026, 6, 8, 10, 5));
            return chatMessage;
        });
        when(aiResultChatResponseRequester.request(eq(diagnosis), eq(List.of(jdResult)), any(), eq(List.of(previousMessage))))
                .thenReturn(aiResponse);

        ChatMessageCreateResponse response = diagnosisChatMessageService.createUserMessage(1L, 100L, request);

        assertThat(response.userMessage().messageId()).isEqualTo(1000L);
        assertThat(response.userMessage().role()).isEqualTo(ChatRole.USER);
        assertThat(response.userMessage().content()).isEqualTo("어떤 공고부터 지원할까?");
        assertThat(response.userMessage().evidenceData()).isNull();
        assertThat(response.assistantMessage().messageId()).isEqualTo(1001L);
        assertThat(response.assistantMessage().role()).isEqualTo(ChatRole.ASSISTANT);
        assertThat(response.assistantMessage().content()).isEqualTo("토스 공고를 먼저 추천합니다.");
        assertThat(response.assistantMessage().evidenceData())
                .isEqualTo("{\"referencedJobIds\":[200],\"reasonCodes\":[\"FIT_SCORE\"],\"usedFields\":[\"reportSummary\",\"jobResults\"]}");
        verify(aiResultChatResponseRequester).request(
                eq(diagnosis),
                eq(List.of(jdResult)),
                any(ChatMessage.class),
                eq(List.of(previousMessage))
        );
        verify(chatMessageRepository, times(2)).save(any(ChatMessage.class));
    }

    @Test
    void createUserMessageThrowsSafeErrorWhenAiChatResponseFails() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        diagnosis.complete("요약", "본문", LocalDateTime.of(2026, 6, 8, 10, 0));
        JDResult jdResult = createJdResult(200L, diagnosis);
        ChatMessageCreateRequest request = new ChatMessageCreateRequest("강점을 알려줘");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));
        when(chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(diagnosis))
                .thenReturn(List.of());
        when(jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis))
                .thenReturn(List.of(jdResult));
        when(chatMessageRepository.save(any(ChatMessage.class))).thenAnswer(invocation -> {
            ChatMessage chatMessage = invocation.getArgument(0);
            ReflectionTestUtils.setField(chatMessage, "id", 1000L);
            ReflectionTestUtils.setField(chatMessage, "createdAt", LocalDateTime.of(2026, 6, 8, 10, 5));
            return chatMessage;
        });
        when(aiResultChatResponseRequester.request(eq(diagnosis), eq(List.of(jdResult)), any(), eq(List.of())))
                .thenThrow(new BusinessException(
                        ErrorCode.AI_CHAT_RESPONSE_FAILED,
                        "AI assistant response is temporarily unavailable."
                ));

        assertThatThrownBy(() -> diagnosisChatMessageService.createUserMessage(1L, 100L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("AI assistant response is temporarily unavailable.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.AI_CHAT_RESPONSE_FAILED);

        verify(chatMessageRepository, times(1)).save(any(ChatMessage.class));
    }

    @Test
    void createUserMessageThrowsDiagnosisNotCompletedWhenDiagnosisIsProcessing() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        diagnosis.startAnalysis(
                "task-123",
                "{\"experienceLevel\":\"NEW\"}",
                LocalDateTime.of(2026, 6, 8, 10, 0)
        );
        ChatMessageCreateRequest request = new ChatMessageCreateRequest("분석 결과를 설명해줘");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));

        assertThatThrownBy(() -> diagnosisChatMessageService.createUserMessage(1L, 100L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis result is not ready for chat.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.DIAGNOSIS_NOT_COMPLETED);

        verify(chatMessageRepository, never()).save(any());
    }

    @Test
    void createUserMessageThrowsDiagnosisNotCompletedWhenDiagnosisFailed() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        diagnosis.fail("AI_TIMEOUT", "분석 시간이 초과되었습니다.", null, null, LocalDateTime.of(2026, 6, 8, 10, 0));
        ChatMessageCreateRequest request = new ChatMessageCreateRequest("실패 이유를 알려줘");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));

        assertThatThrownBy(() -> diagnosisChatMessageService.createUserMessage(1L, 100L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis result is not ready for chat.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.DIAGNOSIS_NOT_COMPLETED);

        verify(chatMessageRepository, never()).save(any());
    }

    @Test
    void createUserMessageThrowsUnauthorizedWhenUserDoesNotExist() {
        ChatMessageCreateRequest request = new ChatMessageCreateRequest("질문");

        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisChatMessageService.createUserMessage(1L, 100L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Authentication is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);

        verify(diagnosisRepository, never()).findById(any());
        verify(chatMessageRepository, never()).save(any());
    }

    private User createUser(Long id, String email) {
        User user = new User(email, "hashed-password", "문석현", null);
        ReflectionTestUtils.setField(user, "id", id);
        return user;
    }

    private Profile createProfile(Long id, User user) {
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ReflectionTestUtils.setField(profile, "id", id);
        return profile;
    }

    private Diagnosis createDiagnosis(Long id, Profile profile) {
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", id);
        return diagnosis;
    }

    private JDResult createJdResult(Long id, Diagnosis diagnosis) {
        JDResult jdResult = new JDResult(
                diagnosis,
                "토스",
                "AI Engineer",
                "채용공고 본문",
                1
        );
        ReflectionTestUtils.setField(jdResult, "id", id);
        return jdResult;
    }

    private ChatMessage createMessage(
            Long id,
            Diagnosis diagnosis,
            ChatRole role,
            String content,
            String evidenceData
    ) {
        ChatMessage chatMessage = new ChatMessage(diagnosis, role, content, evidenceData);
        ReflectionTestUtils.setField(chatMessage, "id", id);
        ReflectionTestUtils.setField(chatMessage, "createdAt", LocalDateTime.of(2026, 6, 8, 10, id.intValue() % 60));
        return chatMessage;
    }
}
