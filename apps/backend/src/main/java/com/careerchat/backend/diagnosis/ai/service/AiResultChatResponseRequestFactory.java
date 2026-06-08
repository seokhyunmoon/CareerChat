package com.careerchat.backend.diagnosis.ai.service;

import com.careerchat.backend.diagnosis.ai.dto.AiResultChatResponseRequest;
import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class AiResultChatResponseRequestFactory {

    private static final int MAX_PREVIOUS_MESSAGES = 20;

    private final ObjectMapper objectMapper;

    public AiResultChatResponseRequestFactory(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public AiResultChatResponseRequest create(
            Diagnosis diagnosis,
            List<JDResult> jdResults,
            ChatMessage userMessage,
            List<ChatMessage> previousMessages
    ) {
        validateResultContext(diagnosis, jdResults);

        return new AiResultChatResponseRequest(
                diagnosis.getId(),
                userMessage.getContent(),
                diagnosis.getReportSummary(),
                diagnosis.getReportContent(),
                jdResults.stream()
                        .map(this::toJobResult)
                        .toList(),
                toPreviousMessages(previousMessages)
        );
    }

    private void validateResultContext(Diagnosis diagnosis, List<JDResult> jdResults) {
        if (isBlank(diagnosis.getReportSummary()) || isBlank(diagnosis.getReportContent()) || jdResults.isEmpty()) {
            throw new BusinessException(
                    ErrorCode.DIAGNOSIS_NOT_COMPLETED,
                    "Diagnosis result is not ready for chat."
            );
        }
    }

    private AiResultChatResponseRequest.JobResult toJobResult(JDResult jdResult) {
        return new AiResultChatResponseRequest.JobResult(
                jdResult.getId(),
                jdResult.getRankOrder(),
                jdResult.getCompanyName(),
                jdResult.getPosition(),
                jdResult.getFitScore(),
                jdResult.getStrengthsSummary(),
                jdResult.getGapsSummary(),
                parseHighlightPoints(jdResult.getHighlightPoints()),
                parseMatchDetails(jdResult.getMatchDetails())
        );
    }

    private List<AiResultChatResponseRequest.PreviousMessage> toPreviousMessages(
            List<ChatMessage> previousMessages
    ) {
        int skipCount = Math.max(0, previousMessages.size() - MAX_PREVIOUS_MESSAGES);

        return previousMessages.stream()
                .skip(skipCount)
                .map(message -> new AiResultChatResponseRequest.PreviousMessage(
                        message.getRole(),
                        message.getContent()
                ))
                .toList();
    }

    private List<String> parseHighlightPoints(String value) {
        if (isBlank(value)) {
            return List.of();
        }

        String trimmed = value.trim();
        try {
            JsonNode root = objectMapper.readTree(trimmed);
            if (root.isArray()) {
                return objectMapper.convertValue(root, new TypeReference<List<String>>() {
                }).stream()
                        .map(String::trim)
                        .filter(point -> !point.isBlank())
                        .toList();
            }
            if (root.isTextual() && !root.asText().isBlank()) {
                return List.of(root.asText().trim());
            }
        } catch (JsonProcessingException ignored) {
            // Non-JSON highlight text is normalized below.
        }

        return trimmed.lines()
                .map(String::trim)
                .map(this::removeListMarker)
                .filter(point -> !point.isBlank())
                .toList();
    }

    private List<Map<String, Object>> parseMatchDetails(String value) {
        if (isBlank(value)) {
            return List.of();
        }

        try {
            JsonNode root = objectMapper.readTree(value);
            JsonNode details = root;
            if (root.has("requirements")) {
                details = root.get("requirements");
            } else if (root.has("requirementMatches")) {
                details = root.get("requirementMatches");
            }

            if (details.isArray()) {
                return objectMapper.convertValue(details, new TypeReference<List<Map<String, Object>>>() {
                });
            }
            if (details.isObject()) {
                return List.of(objectMapper.convertValue(details, new TypeReference<Map<String, Object>>() {
                }));
            }
        } catch (JsonProcessingException ignored) {
            return List.of();
        }

        return List.of();
    }

    private String removeListMarker(String value) {
        return value.replaceFirst("^(?:[-*•]|\\d+[.)])\\s+", "");
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
