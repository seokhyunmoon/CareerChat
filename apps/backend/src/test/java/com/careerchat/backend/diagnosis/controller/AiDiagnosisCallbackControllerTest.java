package com.careerchat.backend.diagnosis.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.doThrow;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.careerchat.backend.diagnosis.service.DiagnosisService;
import com.careerchat.backend.global.config.SecurityConfig;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.global.security.JwtTokenProvider;
import com.careerchat.backend.global.security.RestAuthenticationEntryPoint;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(AiDiagnosisCallbackController.class)
@Import({SecurityConfig.class, RestAuthenticationEntryPoint.class})
class AiDiagnosisCallbackControllerTest {

    private static final String CALLBACK_TOKEN = "careerchat-local-ai-callback-token";

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DiagnosisService diagnosisService;

    @MockitoBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    void completeDiagnosisReturnsOkResponse() throws Exception {
        mockMvc.perform(post("/internal/ai/diagnoses/100/complete")
                        .header("Authorization", "Bearer " + CALLBACK_TOKEN)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "taskId": "task-123",
                                  "reportSummary": "요약",
                                  "reportContent": "본문",
                                  "completedAt": "2026-05-23T12:05:00",
                                  "modelName": "gpt-4.1-mini",
                                  "promptVersion": "diagnosis-report-v1",
                                  "analysisMetadata": "{\\"durationMs\\":300000}",
                                  "jobs": [
                                    {
                                      "jdId": 200,
                                      "rankOrder": 1,
                                      "fitScore": 86.50,
                                      "strengthsSummary": "강점",
                                      "gapsSummary": "부족",
                                      "highlightPoints": "강조",
                                      "matchDetails": "{\\"requirements\\":[{\\"name\\":\\"Spring\\",\\"match\\":\\"HIGH\\"}]}"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").doesNotExist())
                .andExpect(jsonPath("$.message").value("Request succeeded."));

        verify(diagnosisService).completeDiagnosisFromAi(eq(100L), any());
    }

    @Test
    void failDiagnosisReturnsOkResponse() throws Exception {
        mockMvc.perform(post("/internal/ai/diagnoses/100/fail")
                        .header("Authorization", "Bearer " + CALLBACK_TOKEN)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "taskId": "task-123",
                                  "errorCode": "AI_TIMEOUT",
                                  "errorMessage": "분석 시간이 초과되었습니다.",
                                  "failedStep": "REPORT_GENERATION",
                                  "failedAt": "2026-05-23T12:05:00",
                                  "errorDetails": "{\\"retryable\\":true}"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").doesNotExist())
                .andExpect(jsonPath("$.message").value("Request succeeded."));

        verify(diagnosisService).failDiagnosisFromAi(eq(100L), any());
    }

    @Test
    void completeDiagnosisReturnsUnauthorizedWhenCallbackTokenIsMissing() throws Exception {
        mockMvc.perform(post("/internal/ai/diagnoses/100/complete")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(validCompleteRequest()))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Invalid AI callback token."));

        verify(diagnosisService, never()).completeDiagnosisFromAi(any(), any());
    }

    @Test
    void completeDiagnosisReturnsUnauthorizedWhenCallbackTokenIsInvalid() throws Exception {
        mockMvc.perform(post("/internal/ai/diagnoses/100/complete")
                        .header("Authorization", "Bearer invalid-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(validCompleteRequest()))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Invalid AI callback token."));

        verify(diagnosisService, never()).completeDiagnosisFromAi(any(), any());
    }

    @Test
    void completeDiagnosisReturnsForbiddenWhenTaskIdDoesNotMatch() throws Exception {
        doThrow(new BusinessException(ErrorCode.FORBIDDEN, "Invalid AI task id."))
                .when(diagnosisService).completeDiagnosisFromAi(eq(100L), any());

        mockMvc.perform(post("/internal/ai/diagnoses/100/complete")
                        .header("Authorization", "Bearer " + CALLBACK_TOKEN)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(validCompleteRequest()))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("FORBIDDEN"))
                .andExpect(jsonPath("$.message").value("Invalid AI task id."));
    }

    @Test
    void completeDiagnosisReturnsBadRequestWhenRequestIsInvalid() throws Exception {
        mockMvc.perform(post("/internal/ai/diagnoses/100/complete")
                        .header("Authorization", "Bearer " + CALLBACK_TOKEN)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "taskId": "",
                                  "reportSummary": "",
                                  "reportContent": "본문",
                                  "completedAt": null,
                                  "jobs": []
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors").exists());
    }

    private String validCompleteRequest() {
        return """
                {
                  "taskId": "task-123",
                  "reportSummary": "요약",
                  "reportContent": "본문",
                  "completedAt": "2026-05-23T12:05:00",
                  "jobs": [
                    {
                      "jdId": 200,
                      "rankOrder": 1,
                      "fitScore": 86.50
                    }
                  ]
                }
                """;
    }
}
