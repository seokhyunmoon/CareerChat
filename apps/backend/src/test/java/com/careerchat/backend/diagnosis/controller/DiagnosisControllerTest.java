package com.careerchat.backend.diagnosis.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
import com.careerchat.backend.diagnosis.dto.DiagnosisHistoryResponse;
import com.careerchat.backend.diagnosis.dto.DiagnosisResultResponse;
import com.careerchat.backend.diagnosis.service.DiagnosisService;
import com.careerchat.backend.global.config.SecurityConfig;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.global.security.JwtTokenProvider;
import com.careerchat.backend.global.security.RestAuthenticationEntryPoint;
import java.math.BigDecimal;
import java.time.LocalDateTime;
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
                .andExpect(jsonPath("$.data.status").value("PROCESSING"))
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

    @Test
    void getDiagnosisReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.getDiagnosis(1L, 100L)).thenReturn(createResultResponse());

        mockMvc.perform(get("/diagnoses/100")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.diagnosisId").value(100))
                .andExpect(jsonPath("$.data.status").value("COMPLETED"))
                .andExpect(jsonPath("$.data.reportSummary").value("요약"))
                .andExpect(jsonPath("$.data.jobs[0].jdId").value(200))
                .andExpect(jsonPath("$.data.jobs[0].rankOrder").value(1))
                .andExpect(jsonPath("$.data.jobs[0].fitScore").value(86.5))
                .andExpect(jsonPath("$.data.jobs[0].strengths[0].title").value("Spring Boot"))
                .andExpect(jsonPath("$.data.jobs[0].relatedExperiences[0].title").value("CareerChat"))
                .andExpect(jsonPath("$.data.jobs[0].gaps[0].title").value("운영 경험"))
                .andExpect(jsonPath("$.data.jobs[0].resumeHighlights[0].title").value("REST API"))
                .andExpect(jsonPath("$.data.jobs[0].strategyAdvice[0].title").value("필수 요건 보완"))
                .andExpect(jsonPath("$.data.jobs[0].matchDetails.requirements[0].name").value("Spring"))
                .andExpect(jsonPath("$.data.aiTaskId").doesNotExist())
                .andExpect(jsonPath("$.data.profileSnapshot").doesNotExist())
                .andExpect(jsonPath("$.data.analysisMetadata").doesNotExist())
                .andExpect(jsonPath("$.data.errorDetails").doesNotExist())
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void getDiagnosisReturnsUnauthorizedWhenAuthorizationHeaderIsMissing() throws Exception {
        mockMvc.perform(get("/diagnoses/100"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Authentication is required."));
    }

    @Test
    void getDiagnosisReturnsNotFoundWhenDiagnosisDoesNotExist() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.getDiagnosis(1L, 100L))
                .thenThrow(new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Diagnosis not found."));

        mockMvc.perform(get("/diagnoses/100")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("RESOURCE_NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("Diagnosis not found."));
    }

    @Test
    void getDiagnosisReturnsForbiddenWhenDiagnosisBelongsToOtherUser() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.getDiagnosis(1L, 100L))
                .thenThrow(new BusinessException(ErrorCode.FORBIDDEN, "Cannot access this diagnosis."));

        mockMvc.perform(get("/diagnoses/100")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("FORBIDDEN"))
                .andExpect(jsonPath("$.message").value("Cannot access this diagnosis."));
    }

    @Test
    void getDiagnosesReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.getDiagnoses(1L)).thenReturn(createHistoryResponse());

        mockMvc.perform(get("/diagnoses")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.diagnoses[0].diagnosisId").value(101))
                .andExpect(jsonPath("$.data.diagnoses[0].status").value("PROCESSING"))
                .andExpect(jsonPath("$.data.diagnoses[0].companies[0]").value("회사 C"))
                .andExpect(jsonPath("$.data.diagnoses[0].jobCount").value(1))
                .andExpect(jsonPath("$.data.diagnoses[0].topFitScore").doesNotExist())
                .andExpect(jsonPath("$.data.diagnoses[1].diagnosisId").value(100))
                .andExpect(jsonPath("$.data.diagnoses[1].status").value("COMPLETED"))
                .andExpect(jsonPath("$.data.diagnoses[1].companies[0]").value("회사 A"))
                .andExpect(jsonPath("$.data.diagnoses[1].jobsSummary").value("Backend Engineer · AI Engineer"))
                .andExpect(jsonPath("$.data.diagnoses[1].topCompanyName").value("회사 B"))
                .andExpect(jsonPath("$.data.diagnoses[1].topFitScore").value(86.5))
                .andExpect(jsonPath("$.data.diagnoses[1].reportContent").doesNotExist())
                .andExpect(jsonPath("$.data.diagnoses[1].matchDetails").doesNotExist())
                .andExpect(jsonPath("$.data.diagnoses[1].aiTaskId").doesNotExist())
                .andExpect(jsonPath("$.data.diagnoses[1].profileSnapshot").doesNotExist())
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void getDiagnosesReturnsUnauthorizedWhenAuthorizationHeaderIsMissing() throws Exception {
        mockMvc.perform(get("/diagnoses"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Authentication is required."));
    }

    @Test
    void getDiagnosesReturnsEmptyHistory() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(diagnosisService.getDiagnoses(1L)).thenReturn(new DiagnosisHistoryResponse(List.of()));

        mockMvc.perform(get("/diagnoses")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.diagnoses").isEmpty())
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    private DiagnosisCreateResponse createResponse() {
        return new DiagnosisCreateResponse(
                1L,
                DiagnosisStatus.PROCESSING,
                List.of(new DiagnosisCreateResponse.JobResponse(
                        10L,
                        1,
                        "회사 A",
                        "Backend Engineer"
                ))
        );
    }

    private DiagnosisHistoryResponse createHistoryResponse() {
        return new DiagnosisHistoryResponse(List.of(
                new DiagnosisHistoryResponse.DiagnosisSummaryResponse(
                        101L,
                        DiagnosisStatus.PROCESSING,
                        LocalDateTime.of(2026, 5, 23, 12, 10),
                        LocalDateTime.of(2026, 5, 23, 12, 11),
                        null,
                        null,
                        List.of("회사 C"),
                        "Frontend Engineer",
                        1,
                        "회사 C",
                        "Frontend Engineer",
                        null,
                        null
                ),
                new DiagnosisHistoryResponse.DiagnosisSummaryResponse(
                        100L,
                        DiagnosisStatus.COMPLETED,
                        LocalDateTime.of(2026, 5, 23, 11, 58),
                        LocalDateTime.of(2026, 5, 23, 11, 59),
                        LocalDateTime.of(2026, 5, 23, 12, 0),
                        null,
                        List.of("회사 A", "회사 B"),
                        "Backend Engineer · AI Engineer",
                        2,
                        "회사 B",
                        "AI Engineer",
                        new BigDecimal("86.50"),
                        null
                )
        ));
    }

    private DiagnosisResultResponse createResultResponse() {
        return new DiagnosisResultResponse(
                100L,
                DiagnosisStatus.COMPLETED,
                LocalDateTime.of(2026, 5, 23, 11, 58),
                LocalDateTime.of(2026, 5, 23, 11, 59),
                LocalDateTime.of(2026, 5, 23, 12, 0),
                null,
                "요약",
                "본문",
                null,
                null,
                List.of(new DiagnosisResultResponse.JobResultResponse(
                        200L,
                        1,
                        1,
                        "회사 A",
                        "Backend Engineer",
                        new BigDecimal("86.50"),
                        "강점",
                        "부족",
                        "강조",
                        "[{\"title\":\"Spring Boot\",\"description\":\"REST API 경험\"}]",
                        "[{\"title\":\"CareerChat\",\"description\":\"관련 프로젝트\"}]",
                        "[{\"title\":\"운영 경험\",\"description\":\"근거 부족\"}]",
                        "[{\"title\":\"REST API\",\"description\":\"강조 포인트\"}]",
                        "[{\"title\":\"필수 요건 보완\",\"description\":\"운영 경험 보완 필요\"}]",
                        "{\"requirements\":[{\"name\":\"Spring\",\"match\":\"HIGH\"}]}"
                ))
        );
    }
}
