package com.careerchat.backend.diagnosis.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.careerchat.backend.diagnosis.domain.ChatRole;
import com.careerchat.backend.diagnosis.dto.ChatMessageCreateResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessageResponse;
import com.careerchat.backend.diagnosis.dto.ChatMessagesResponse;
import com.careerchat.backend.diagnosis.service.DiagnosisChatMessageService;
import com.careerchat.backend.global.config.SecurityConfig;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.global.security.JwtTokenProvider;
import com.careerchat.backend.global.security.RestAuthenticationEntryPoint;
import java.time.LocalDateTime;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(DiagnosisChatMessageController.class)
@Import({SecurityConfig.class, RestAuthenticationEntryPoint.class})
class DiagnosisChatMessageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DiagnosisChatMessageService diagnosisChatMessageService;

    @MockitoBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    void getMessagesReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.getMessages(1L, 100L)).thenReturn(new ChatMessagesResponse(List.of(
                new ChatMessageResponse(
                        1000L,
                        ChatRole.USER,
                        "어떤 공고부터 지원할까?",
                        null,
                        LocalDateTime.of(2026, 6, 8, 10, 0)
                ),
                new ChatMessageResponse(
                        1001L,
                        ChatRole.ASSISTANT,
                        "첫 번째 공고를 추천합니다.",
                        "{\"jdId\":1}",
                        LocalDateTime.of(2026, 6, 8, 10, 1)
                )
        )));

        mockMvc.perform(get("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.messages[0].messageId").value(1000))
                .andExpect(jsonPath("$.data.messages[0].role").value("USER"))
                .andExpect(jsonPath("$.data.messages[0].content").value("어떤 공고부터 지원할까?"))
                .andExpect(jsonPath("$.data.messages[1].messageId").value(1001))
                .andExpect(jsonPath("$.data.messages[1].role").value("ASSISTANT"))
                .andExpect(jsonPath("$.data.messages[1].evidenceData.jdId").value(1))
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void getMessagesReturnsUnauthorizedWhenAuthorizationHeaderIsMissing() throws Exception {
        mockMvc.perform(get("/diagnoses/100/chat/messages"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Authentication is required."));
    }

    @Test
    void getMessagesReturnsForbiddenWhenDiagnosisBelongsToOtherUser() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.getMessages(1L, 100L))
                .thenThrow(new BusinessException(ErrorCode.FORBIDDEN, "Cannot access this diagnosis."));

        mockMvc.perform(get("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("FORBIDDEN"))
                .andExpect(jsonPath("$.message").value("Cannot access this diagnosis."));
    }

    @Test
    void getMessagesReturnsNotFoundWhenDiagnosisDoesNotExist() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.getMessages(1L, 100L))
                .thenThrow(new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Diagnosis not found."));

        mockMvc.perform(get("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("RESOURCE_NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("Diagnosis not found."));
    }

    @Test
    void createUserMessageReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.createUserMessage(eq(1L), eq(100L), any()))
                .thenReturn(new ChatMessageCreateResponse(
                        new ChatMessageResponse(
                                1000L,
                                ChatRole.USER,
                                "강점을 더 자세히 알려줘",
                                null,
                                LocalDateTime.of(2026, 6, 8, 10, 0)
                        ),
                        new ChatMessageResponse(
                                1001L,
                                ChatRole.ASSISTANT,
                                "RAG 구성 요소 설계 경험을 중심으로 강조하면 좋습니다.",
                                "{\"referencedJobIds\":[200],\"reasonCodes\":[\"STRENGTHS\"],\"usedFields\":[\"jobResults\"]}",
                                LocalDateTime.of(2026, 6, 8, 10, 1)
                        )
                ));

        mockMvc.perform(post("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "content": "강점을 더 자세히 알려줘"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.userMessage.messageId").value(1000))
                .andExpect(jsonPath("$.data.userMessage.role").value("USER"))
                .andExpect(jsonPath("$.data.userMessage.content").value("강점을 더 자세히 알려줘"))
                .andExpect(jsonPath("$.data.assistantMessage.messageId").value(1001))
                .andExpect(jsonPath("$.data.assistantMessage.role").value("ASSISTANT"))
                .andExpect(jsonPath("$.data.assistantMessage.content").value("RAG 구성 요소 설계 경험을 중심으로 강조하면 좋습니다."))
                .andExpect(jsonPath("$.data.assistantMessage.evidenceData.referencedJobIds[0]").value(200))
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void createUserMessageReturnsBadRequestWhenContentIsBlank() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);

        mockMvc.perform(post("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "content": ""
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors.content").exists());
    }

    @Test
    void createUserMessageReturnsConflictWhenDiagnosisIsNotCompleted() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.createUserMessage(eq(1L), eq(100L), any()))
                .thenThrow(new BusinessException(
                        ErrorCode.DIAGNOSIS_NOT_COMPLETED,
                        "Diagnosis result is not ready for chat."
                ));

        mockMvc.perform(post("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "content": "분석 결과를 알려줘"
                                }
                                """))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("DIAGNOSIS_NOT_COMPLETED"))
                .andExpect(jsonPath("$.message").value("Diagnosis result is not ready for chat."));
    }

    @Test
    void createUserMessageReturnsServiceUnavailableWhenAiChatResponseFails() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisChatMessageService.createUserMessage(eq(1L), eq(100L), any()))
                .thenThrow(new BusinessException(
                        ErrorCode.AI_CHAT_RESPONSE_FAILED,
                        "AI assistant response is temporarily unavailable."
                ));

        mockMvc.perform(post("/diagnoses/100/chat/messages")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "content": "분석 결과를 알려줘"
                                }
                                """))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("AI_CHAT_RESPONSE_FAILED"))
                .andExpect(jsonPath("$.message").value("AI assistant response is temporarily unavailable."));
    }
}
