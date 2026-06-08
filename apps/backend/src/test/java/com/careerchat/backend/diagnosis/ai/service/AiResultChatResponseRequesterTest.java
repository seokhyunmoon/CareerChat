package com.careerchat.backend.diagnosis.ai.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClient;
import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClientException;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AiResultChatResponseRequesterTest {

    private AiResultChatResponseRequestFactory requestFactory;
    private AiAnalysisClient aiAnalysisClient;
    private AiResultChatResponseRequester requester;

    @BeforeEach
    void setUp() {
        requestFactory = mock(AiResultChatResponseRequestFactory.class);
        aiAnalysisClient = mock(AiAnalysisClient.class);
        requester = new AiResultChatResponseRequester(requestFactory, aiAnalysisClient);
    }

    @Test
    void requestDelegatesToAiClient() {
        Diagnosis diagnosis = mock(Diagnosis.class);
        JDResult jdResult = mock(JDResult.class);
        ChatMessage userMessage = mock(ChatMessage.class);
        ChatMessage previousMessage = mock(ChatMessage.class);
        AiResultChatResponseRequest aiRequest = new AiResultChatResponseRequest(
                100L,
                "질문",
                "요약",
                "본문",
                List.of(),
                List.of(new AiResultChatResponseRequest.PreviousMessage(ChatRole.USER, "이전 질문"))
        );
        AiResultChatResponse aiResponse = new AiResultChatResponse(
                "답변",
                new AiResultChatResponse.EvidenceData(List.of(200L), List.of("STRENGTH"), List.of("jobResults")),
                "groq",
                "llama-3.1",
                "result_chat_response",
                "v1"
        );

        when(requestFactory.create(diagnosis, List.of(jdResult), userMessage, List.of(previousMessage)))
                .thenReturn(aiRequest);
        when(aiAnalysisClient.createResultChatResponse(aiRequest)).thenReturn(aiResponse);

        AiResultChatResponse response = requester.request(
                diagnosis,
                List.of(jdResult),
                userMessage,
                List.of(previousMessage)
        );

        assertThat(response).isSameAs(aiResponse);
        verify(aiAnalysisClient).createResultChatResponse(aiRequest);
    }

    @Test
    void requestThrowsSafeBusinessExceptionWhenAiClientFails() {
        Diagnosis diagnosis = mock(Diagnosis.class);
        ChatMessage userMessage = mock(ChatMessage.class);
        AiResultChatResponseRequest aiRequest = new AiResultChatResponseRequest(
                100L,
                "질문",
                "요약",
                "본문",
                List.of(),
                List.of()
        );

        when(requestFactory.create(diagnosis, List.of(), userMessage, List.of())).thenReturn(aiRequest);
        when(aiAnalysisClient.createResultChatResponse(aiRequest))
                .thenThrow(new AiAnalysisClientException("provider raw error"));

        assertThatThrownBy(() -> requester.request(diagnosis, List.of(), userMessage, List.of()))
                .isInstanceOf(BusinessException.class)
                .hasMessage("AI assistant response is temporarily unavailable.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.AI_CHAT_RESPONSE_FAILED);
    }
}
