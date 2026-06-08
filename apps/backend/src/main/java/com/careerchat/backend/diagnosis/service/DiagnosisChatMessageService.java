package com.careerchat.backend.diagnosis.service;

import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.service.AiResultChatResponseRequester;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateRequest;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessagesResponse;
import com.careerchat.backend.diagnosis.repository.ChatMessageRepository;
import com.careerchat.backend.diagnosis.repository.DiagnosisRepository;
import com.careerchat.backend.diagnosis.repository.JDResultRepository;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DiagnosisChatMessageService {

    private final UserRepository userRepository;
    private final DiagnosisRepository diagnosisRepository;
    private final JDResultRepository jdResultRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final AiResultChatResponseRequester aiResultChatResponseRequester;
    private final ObjectMapper objectMapper;

    public DiagnosisChatMessageService(
            UserRepository userRepository,
            DiagnosisRepository diagnosisRepository,
            JDResultRepository jdResultRepository,
            ChatMessageRepository chatMessageRepository,
            AiResultChatResponseRequester aiResultChatResponseRequester,
            ObjectMapper objectMapper
    ) {
        this.userRepository = userRepository;
        this.diagnosisRepository = diagnosisRepository;
        this.jdResultRepository = jdResultRepository;
        this.chatMessageRepository = chatMessageRepository;
        this.aiResultChatResponseRequester = aiResultChatResponseRequester;
        this.objectMapper = objectMapper;
    }

    @Transactional(readOnly = true)
    public ChatMessagesResponse getMessages(Long userId, Long diagnosisId) {
        User user = getCurrentUser(userId);
        Diagnosis diagnosis = getOwnedDiagnosis(user, diagnosisId);

        return ChatMessagesResponse.from(
                chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(diagnosis)
        );
    }

    @Transactional
    public ChatMessageCreateResponse createUserMessage(
            Long userId,
            Long diagnosisId,
            ChatMessageCreateRequest request
    ) {
        User user = getCurrentUser(userId);
        Diagnosis diagnosis = getOwnedDiagnosis(user, diagnosisId);
        validateCompletedDiagnosis(diagnosis);

        List<ChatMessage> previousMessages = chatMessageRepository.findAllByDiagnosisOrderByCreatedAtAscIdAsc(
                diagnosis
        );
        List<JDResult> jdResults = jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis);
        ChatMessage userMessage = chatMessageRepository.save(new ChatMessage(
                diagnosis,
                ChatRole.USER,
                request.content(),
                null
        ));

        AiResultChatResponse aiResponse = aiResultChatResponseRequester.request(
                diagnosis,
                jdResults,
                userMessage,
                previousMessages
        );
        ChatMessage assistantMessage = chatMessageRepository.save(new ChatMessage(
                diagnosis,
                ChatRole.ASSISTANT,
                aiResponse.content(),
                writeEvidenceData(aiResponse)
        ));

        return ChatMessageCreateResponse.of(userMessage, assistantMessage);
    }

    private User getCurrentUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "Authentication is required."));
    }

    private Diagnosis getOwnedDiagnosis(User user, Long diagnosisId) {
        Diagnosis diagnosis = diagnosisRepository.findById(diagnosisId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Diagnosis not found."));

        validateDiagnosisOwner(user, diagnosis);

        return diagnosis;
    }

    private void validateDiagnosisOwner(User user, Diagnosis diagnosis) {
        Long ownerId = diagnosis.getProfile().getUser().getId();
        if (!Objects.equals(user.getId(), ownerId)) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "Cannot access this diagnosis.");
        }
    }

    private void validateCompletedDiagnosis(Diagnosis diagnosis) {
        if (diagnosis.getStatus() != DiagnosisStatus.COMPLETED) {
            throw new BusinessException(
                    ErrorCode.DIAGNOSIS_NOT_COMPLETED,
                    "Diagnosis result is not ready for chat."
            );
        }
    }

    private String writeEvidenceData(AiResultChatResponse aiResponse) {
        try {
            return objectMapper.writeValueAsString(aiResponse.evidenceData());
        } catch (JsonProcessingException exception) {
            throw new BusinessException(
                    ErrorCode.AI_CHAT_RESPONSE_FAILED,
                    "AI assistant response is temporarily unavailable."
            );
        }
    }
}
