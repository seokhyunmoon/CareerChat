package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.ChatMessage;
import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.fasterxml.jackson.annotation.JsonRawValue;
import java.time.LocalDateTime;

public record ChatMessageResponse(
        Long messageId,
        ChatRole role,
        String content,
        @JsonRawValue String evidenceData,
        LocalDateTime createdAt
) {

    @JsonRawValue
    public String evidenceData() {
        return evidenceData;
    }

    public static ChatMessageResponse from(ChatMessage chatMessage) {
        return new ChatMessageResponse(
                chatMessage.getId(),
                chatMessage.getRole(),
                chatMessage.getContent(),
                chatMessage.getEvidenceData(),
                chatMessage.getCreatedAt()
        );
    }
}
