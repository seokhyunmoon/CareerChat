package com.careerchat.backend.diagnosis.controller;

import com.careerchat.backend.diagnosis.dto.ChatMessageCreateRequest;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessagesResponse;
import com.careerchat.backend.diagnosis.service.DiagnosisChatMessageService;
import com.careerchat.backend.global.common.ApiResponse;
import com.careerchat.backend.global.security.AuthenticatedUser;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DiagnosisChatMessageController {

    private final DiagnosisChatMessageService diagnosisChatMessageService;

    public DiagnosisChatMessageController(DiagnosisChatMessageService diagnosisChatMessageService) {
        this.diagnosisChatMessageService = diagnosisChatMessageService;
    }

    @GetMapping("/diagnoses/{diagnosisId}/chat/messages")
    public ApiResponse<ChatMessagesResponse> getMessages(
            @AuthenticationPrincipal AuthenticatedUser authenticatedUser,
            @PathVariable Long diagnosisId
    ) {
        ChatMessagesResponse response = diagnosisChatMessageService.getMessages(
                authenticatedUser.userId(),
                diagnosisId
        );

        return ApiResponse.success(response);
    }

    @PostMapping("/diagnoses/{diagnosisId}/chat/messages")
    public ApiResponse<ChatMessageCreateResponse> createUserMessage(
            @AuthenticationPrincipal AuthenticatedUser authenticatedUser,
            @PathVariable Long diagnosisId,
            @Valid @RequestBody ChatMessageCreateRequest request
    ) {
        ChatMessageCreateResponse response = diagnosisChatMessageService.createUserMessage(
                authenticatedUser.userId(),
                diagnosisId,
                request
        );

        return ApiResponse.success(response);
    }
}
