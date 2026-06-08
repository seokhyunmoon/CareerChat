package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.ChatMessage;

public record ChatMessageCreateResponse(
        ChatMessageResponse userMessage,
        ChatMessageResponse assistantMessage
) {

    public static ChatMessageCreateResponse of(ChatMessage userMessage, ChatMessage assistantMessage) {
        return new ChatMessageCreateResponse(
                ChatMessageResponse.from(userMessage),
                ChatMessageResponse.from(assistantMessage)
        );
    }
}
