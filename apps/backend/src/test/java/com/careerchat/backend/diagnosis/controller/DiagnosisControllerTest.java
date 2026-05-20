package com.careerchat.backend.diagnosis.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
import com.careerchat.backend.diagnosis.service.DiagnosisService;
import com.careerchat.backend.global.config.SecurityConfig;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.global.security.JwtTokenProvider;
import com.careerchat.backend.global.security.RestAuthenticationEntryPoint;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(DiagnosisController.class)
@Import({SecurityConfig.class, RestAuthenticationEntryPoint.class})
class DiagnosisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DiagnosisService diagnosisService;

    @MockitoBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    void createDiagnosisReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.createDiagnosis(eq(1L), any())).thenReturn(createResponse());

        mockMvc.perform(post("/diagnoses")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": [
                                    {
                                      "companyName": "회사 A",
                                      "position": "Backend Engineer",
                                      "content": "백엔드 공고 내용"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.diagnosisId").value(1))
                .andExpect(jsonPath("$.data.status").value("PENDING"))
                .andExpect(jsonPath("$.data.jobs[0].jdId").value(10))
                .andExpect(jsonPath("$.data.jobs[0].displayOrder").value(1))
                .andExpect(jsonPath("$.data.jobs[0].companyName").value("회사 A"))
                .andExpect(jsonPath("$.data.jobs[0].position").value("Backend Engineer"))
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void createDiagnosisReturnsUnauthorizedWhenAuthorizationHeaderIsMissing() throws Exception {
        mockMvc.perform(post("/diagnoses")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": [
                                    {
                                      "companyName": "회사 A",
                                      "position": "Backend Engineer",
                                      "content": "백엔드 공고 내용"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Authentication is required."));
    }

    @Test
    void createDiagnosisReturnsProfileNotFoundWhenProfileDoesNotExist() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.createDiagnosis(eq(1L), any()))
                .thenThrow(new BusinessException(ErrorCode.PROFILE_NOT_FOUND));

        mockMvc.perform(post("/diagnoses")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": [
                                    {
                                      "companyName": "회사 A",
                                      "position": "Backend Engineer",
                                      "content": "백엔드 공고 내용"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("PROFILE_NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("Profile not found."));
    }

    @Test
    void createDiagnosisReturnsBadRequestWhenJobsAreEmpty() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);

        mockMvc.perform(post("/diagnoses")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": []
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors.jobs").exists());
    }

    @Test
    void createDiagnosisReturnsBadRequestWhenJobsAreMoreThanThree() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);

        mockMvc.perform(post("/diagnoses")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": [
                                    {
                                      "companyName": "회사 A",
                                      "position": "Backend Engineer",
                                      "content": "백엔드 공고 내용"
                                    },
                                    {
                                      "companyName": "회사 B",
                                      "position": "Frontend Engineer",
                                      "content": "프론트엔드 공고 내용"
                                    },
                                    {
                                      "companyName": "회사 C",
                                      "position": "AI Engineer",
                                      "content": "AI 공고 내용"
                                    },
                                    {
                                      "companyName": "회사 D",
                                      "position": "Data Engineer",
                                      "content": "데이터 공고 내용"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors.jobs").exists());
    }

    @Test
    void createDiagnosisReturnsBadRequestWhenJobFieldsAreInvalid() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);

        mockMvc.perform(post("/diagnoses")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "jobs": [
                                    {
                                      "companyName": "",
                                      "position": "Backend Engineer",
                                      "content": ""
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors").exists());
    }

    private DiagnosisCreateResponse createResponse() {
        return new DiagnosisCreateResponse(
                1L,
                DiagnosisStatus.PENDING,
                List.of(new DiagnosisCreateResponse.JobResponse(
                        10L,
                        1,
                        "회사 A",
                        "Backend Engineer"
                ))
        );
    }
}