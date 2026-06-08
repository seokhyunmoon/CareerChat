package com.careerchat.backend.diagnosis.dto;

import com.careerchat.backend.diagnosis.domain.ChatMessage;
import java.util.List;

public record ChatMessagesResponse(
        List<ChatMessageResponse> messages
) {

    public static ChatMessagesResponse from(List<ChatMessage> chatMessages) {
        return new ChatMessagesResponse(
                chatMessages.stream()
                        .map(ChatMessageResponse::from)
                        .toList()
        );
    }
}
