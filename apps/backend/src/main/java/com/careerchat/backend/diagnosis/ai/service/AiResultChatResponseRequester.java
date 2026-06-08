package com.careerchat.backend.diagnosis.ai.service;

import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClient;
import com.careerchat.backend.diagnosis.ai.client.AiAnalysisClientException;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponse;
import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class AiResultChatResponseRequester {

    private static final String CHAT_RESPONSE_FAILED_MESSAGE = "AI assistant response is temporarily unavailable.";

    private final AiResultChatResponseRequestFactory requestFactory;
    private final AiAnalysisClient aiAnalysisClient;

    public AiResultChatResponseRequester(
            AiResultChatResponseRequestFactory requestFactory,
            AiAnalysisClient aiAnalysisClient
    ) {
        this.requestFactory = requestFactory;
        this.aiAnalysisClient = aiAnalysisClient;
    }

    public AiResultChatResponse request(
            Diagnosis diagnosis,
            List<JDResult> jdResults,
            ChatMessage userMessage,
            List<ChatMessage> previousMessages
    ) {
        AiResultChatResponseRequest request = requestFactory.create(
                diagnosis,
                jdResults,
                userMessage,
                previousMessages
        );

        try {
            return aiAnalysisClient.createResultChatResponse(request);
        } catch (AiAnalysisClientException exception) {
            throw new BusinessException(ErrorCode.AI_CHAT_RESPONSE_FAILED, CHAT_RESPONSE_FAILED_MESSAGE);
        }
    }
}
