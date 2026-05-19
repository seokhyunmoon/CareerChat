package com.careerchat.backend.profile.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.careerchat.backend.global.config.SecurityConfig;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.global.security.JwtTokenProvider;
import com.careerchat.backend.global.security.RestAuthenticationEntryPoint;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.dto.ProfileResponse;
import com.careerchat.backend.profile.service.ProfileService;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(ProfileController.class)
@Import({SecurityConfig.class, RestAuthenticationEntryPoint.class})
class ProfileControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ProfileService profileService;

    @MockitoBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    void getProfileReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(profileService.getProfile(1L)).thenReturn(createProfileResponse());

        mockMvc.perform(get("/profile")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.profileId").value(1))
                .andExpect(jsonPath("$.data.experienceLevel").value("NEW"))
                .andExpect(jsonPath("$.data.education[0].schoolName").value("Yonsei University"))
                .andExpect(jsonPath("$.data.projects[0].projectName").value("CareerChat"))
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void getProfileReturnsProfileNotFoundWhenProfileDoesNotExist() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(profileService.getProfile(1L)).thenThrow(new BusinessException(ErrorCode.PROFILE_NOT_FOUND));

        mockMvc.perform(get("/profile")
                        .header("Authorization", "Bearer access-token"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("PROFILE_NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("Profile not found."));
    }

    @Test
    void getProfileReturnsUnauthorizedWhenAuthorizationHeaderIsMissing() throws Exception {
        mockMvc.perform(get("/profile"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
                .andExpect(jsonPath("$.message").value("Authentication is required."));
    }

    @Test
    void saveProfileReturnsOkResponse() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);
        when(profileService.saveProfile(eq(1L), any())).thenReturn(createProfileResponse());

        mockMvc.perform(put("/profile")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "experienceLevel": "NEW",
                                  "education": [
                                    {
                                      "schoolName": "Yonsei University",
                                      "gradStatus": "EXPECTED",
                                      "degree": "Bachelor",
                                      "major": "Applied Information Engineering",
                                      "startDate": "2019-09-01",
                                      "endDate": null
                                    }
                                  ],
                                  "workExperiences": [
                                    {
                                      "companyName": "A*STAR IHPC",
                                      "employmentType": "INTERN",
                                      "position": "Research Intern",
                                      "startDate": "2025-09-01",
                                      "endDate": "2025-12-01",
                                      "description": "AI research internship."
                                    }
                                  ],
                                  "projects": [
                                    {
                                      "projectName": "CareerChat",
                                      "description": "Career analysis service."
                                    }
                                  ],
                                  "achievements": [
                                    {
                                      "title": "OPIc IH",
                                      "issuer": "ACTFL",
                                      "scoreOrGrade": "IH",
                                      "acquiredDate": "2025-03-01"
                                    }
                                  ]
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.profileId").value(1))
                .andExpect(jsonPath("$.data.experienceLevel").value("NEW"))
                .andExpect(jsonPath("$.data.workExperiences[0].companyName").value("A*STAR IHPC"))
                .andExpect(jsonPath("$.data.achievements[0].title").value("OPIc IH"))
                .andExpect(jsonPath("$.message").value("Request succeeded."));
    }

    @Test
    void saveProfileReturnsBadRequestWhenRequestIsInvalid() throws Exception {
        when(jwtTokenProvider.validateAccessToken("access-token")).thenReturn(true);
        when(jwtTokenProvider.getUserId("access-token")).thenReturn(1L);

        mockMvc.perform(put("/profile")
                        .header("Authorization", "Bearer access-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "experienceLevel": null,
                                  "education": [],
                                  "workExperiences": [],
                                  "projects": [],
                                  "achievements": []
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value("INVALID_INPUT"))
                .andExpect(jsonPath("$.errors.experienceLevel").exists())
                .andExpect(jsonPath("$.errors.education").exists());
    }

    private ProfileResponse createProfileResponse() {
        return new ProfileResponse(
                1L,
                ExperienceLevel.NEW,
                List.of(new ProfileResponse.EducationResponse(
                        1L,
                        "Yonsei University",
                        "EXPECTED",
                        "Bachelor",
                        "Applied Information Engineering",
                        LocalDate.of(2019, 9, 1),
                        null
                )),
                List.of(new ProfileResponse.WorkExperienceResponse(
                        1L,
                        "A*STAR IHPC",
                        "INTERN",
                        "Research Intern",
                        LocalDate.of(2025, 9, 1),
                        LocalDate.of(2025, 12, 1),
                        "AI research internship."
                )),
                List.of(new ProfileResponse.ProjectResponse(
                        1L,
                        "CareerChat",
                        "Career analysis service."
                )),
                List.of(new ProfileResponse.AchievementResponse(
                        1L,
                        "OPIc IH",
                        "ACTFL",
                        "IH",
                        LocalDate.of(2025, 3, 1)
                ))
        );
    }
}
