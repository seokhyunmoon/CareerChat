package com.careerchat.backend.diagnosis.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.diagnosis.domain.Diagnosis;
import com.careerchat.backend.diagnosis.domain.DiagnosisStatus;
import com.careerchat.backend.diagnosis.domain.JDResult;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateRequest;
import com.careerchat.backend.diagnosis.dto.DiagnosisCreateResponse;
import com.careerchat.backend.diagnosis.dto.DiagnosisResultResponse;
import com.careerchat.backend.diagnosis.repository.DiagnosisRepository;
import com.careerchat.backend.diagnosis.repository.JDResultRepository;
import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.repository.ProfileRepository;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class DiagnosisServiceTest {

    private UserRepository userRepository;
    private ProfileRepository profileRepository;
    private DiagnosisRepository diagnosisRepository;
    private JDResultRepository jdResultRepository;
    private DiagnosisService diagnosisService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        profileRepository = mock(ProfileRepository.class);
        diagnosisRepository = mock(DiagnosisRepository.class);
        jdResultRepository = mock(JDResultRepository.class);
        diagnosisService = new DiagnosisService(
                userRepository,
                profileRepository,
                diagnosisRepository,
                jdResultRepository
        );
    }

    @Test
    void createDiagnosisCreatesDiagnosisAndJdResults() {
        User user = new User("user@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        DiagnosisCreateRequest request = createRequest(2);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));
        when(diagnosisRepository.save(any(Diagnosis.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(jdResultRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));

        DiagnosisCreateResponse response = diagnosisService.createDiagnosis(1L, request);

        assertThat(response.status()).isEqualTo(DiagnosisStatus.PENDING);
        assertThat(response.jobs()).hasSize(2);
        assertThat(response.jobs().get(0).displayOrder()).isEqualTo(1);
        assertThat(response.jobs().get(0).companyName()).isEqualTo("회사 1");
        assertThat(response.jobs().get(1).displayOrder()).isEqualTo(2);
        assertThat(response.jobs().get(1).companyName()).isEqualTo("회사 2");
        verify(diagnosisRepository).save(any(Diagnosis.class));
        verify(jdResultRepository).saveAll(any());
    }

    @Test
    void createDiagnosisAllowsSingleJobPosting() {
        User user = new User("single@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        DiagnosisCreateRequest request = createRequest(1);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));
        when(diagnosisRepository.save(any(Diagnosis.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(jdResultRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));

        DiagnosisCreateResponse response = diagnosisService.createDiagnosis(1L, request);

        assertThat(response.jobs()).hasSize(1);
        assertThat(response.jobs().getFirst().displayOrder()).isEqualTo(1);
    }

    @Test
    void createDiagnosisThrowsProfileNotFoundWhenProfileDoesNotExist() {
        User user = new User("missing-profile@example.com", "hashed-password", "문석현", null);
        DiagnosisCreateRequest request = createRequest(1);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisService.createDiagnosis(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Profile not found.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.PROFILE_NOT_FOUND);

        verify(diagnosisRepository, never()).save(any());
        verify(jdResultRepository, never()).saveAll(any());
    }

    @Test
    void createDiagnosisThrowsUnauthorizedWhenUserDoesNotExist() {
        DiagnosisCreateRequest request = createRequest(1);

        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisService.createDiagnosis(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Authentication is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);

        verify(profileRepository, never()).findByUser(any());
        verify(diagnosisRepository, never()).save(any());
        verify(jdResultRepository, never()).saveAll(any());
    }

    @Test
    void createDiagnosisThrowsInvalidInputWhenJobsAreEmpty() {
        User user = new User("empty-jobs@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        DiagnosisCreateRequest request = new DiagnosisCreateRequest(List.of());

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));

        assertThatThrownBy(() -> diagnosisService.createDiagnosis(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis requires 1 to 3 job postings.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.INVALID_INPUT);

        verify(diagnosisRepository, never()).save(any());
        verify(jdResultRepository, never()).saveAll(any());
    }

    @Test
    void createDiagnosisThrowsInvalidInputWhenJobsAreMoreThanThree() {
        User user = new User("too-many-jobs@example.com", "hashed-password", "문석현", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        DiagnosisCreateRequest request = createRequest(4);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));

        assertThatThrownBy(() -> diagnosisService.createDiagnosis(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis requires 1 to 3 job postings.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.INVALID_INPUT);

        verify(diagnosisRepository, never()).save(any());
        verify(jdResultRepository, never()).saveAll(any());
    }

    @Test
    void getDiagnosisReturnsDiagnosisResult() {
        User user = createUser(1L, "owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        LocalDateTime completedAt = LocalDateTime.of(2026, 5, 23, 12, 0);
        diagnosis.complete("요약", "본문", completedAt);
        JDResult jdResult = createJdResult(200L, diagnosis);
        jdResult.updateAnalysisResult(
                1,
                new BigDecimal("86.50"),
                "강점",
                "부족",
                "강조",
                "{\"requirements\":[{\"name\":\"Spring\",\"match\":\"HIGH\"}]}"
        );

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));
        when(jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis))
                .thenReturn(List.of(jdResult));

        DiagnosisResultResponse response = diagnosisService.getDiagnosis(1L, 100L);

        assertThat(response.diagnosisId()).isEqualTo(100L);
        assertThat(response.status()).isEqualTo(DiagnosisStatus.COMPLETED);
        assertThat(response.reportSummary()).isEqualTo("요약");
        assertThat(response.reportContent()).isEqualTo("본문");
        assertThat(response.completedAt()).isEqualTo(completedAt);
        assertThat(response.jobs()).hasSize(1);
        assertThat(response.jobs().getFirst().jdId()).isEqualTo(200L);
        assertThat(response.jobs().getFirst().rankOrder()).isEqualTo(1);
        assertThat(response.jobs().getFirst().fitScore()).isEqualByComparingTo("86.50");
        assertThat(response.jobs().getFirst().matchDetails()).contains("Spring");
    }

    @Test
    void getDiagnosisReturnsProcessingStatusWithDraftJobs() {
        User user = createUser(1L, "processing-owner@example.com");
        Profile profile = createProfile(10L, user);
        Diagnosis diagnosis = createDiagnosis(100L, profile);
        diagnosis.startAnalysis(
                "task-123",
                "{\"experienceLevel\":\"NEW\"}",
                LocalDateTime.of(2026, 5, 23, 12, 0)
        );
        JDResult jdResult = createJdResult(200L, diagnosis);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));
        when(jdResultRepository.findAllByDiagnosisOrderByDisplayOrderAsc(diagnosis))
                .thenReturn(List.of(jdResult));

        DiagnosisResultResponse response = diagnosisService.getDiagnosis(1L, 100L);

        assertThat(response.status()).isEqualTo(DiagnosisStatus.PROCESSING);
        assertThat(response.reportSummary()).isNull();
        assertThat(response.jobs()).hasSize(1);
        assertThat(response.jobs().getFirst().companyName()).isEqualTo("회사 A");
        assertThat(response.jobs().getFirst().fitScore()).isNull();
    }

    @Test
    void getDiagnosisThrowsResourceNotFoundWhenDiagnosisDoesNotExist() {
        User user = createUser(1L, "missing-diagnosis@example.com");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisService.getDiagnosis(1L, 100L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Diagnosis not found.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.RESOURCE_NOT_FOUND);

        verify(jdResultRepository, never()).findAllByDiagnosisOrderByDisplayOrderAsc(any());
    }

    @Test
    void getDiagnosisThrowsForbiddenWhenDiagnosisBelongsToOtherUser() {
        User user = createUser(1L, "requester@example.com");
        User otherUser = createUser(2L, "owner@example.com");
        Profile profile = createProfile(10L, otherUser);
        Diagnosis diagnosis = createDiagnosis(100L, profile);

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(diagnosisRepository.findById(100L)).thenReturn(Optional.of(diagnosis));

        assertThatThrownBy(() -> diagnosisService.getDiagnosis(1L, 100L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Cannot access this diagnosis.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.FORBIDDEN);

        verify(jdResultRepository, never()).findAllByDiagnosisOrderByDisplayOrderAsc(any());
    }

    @Test
    void getDiagnosisThrowsUnauthorizedWhenUserDoesNotExist() {
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> diagnosisService.getDiagnosis(1L, 100L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Authentication is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);

        verify(diagnosisRepository, never()).findById(any());
        verify(jdResultRepository, never()).findAllByDiagnosisOrderByDisplayOrderAsc(any());
    }

    private DiagnosisCreateRequest createRequest(int jobCount) {
        List<DiagnosisCreateRequest.JobRequest> jobs = java.util.stream.IntStream.rangeClosed(1, jobCount)
                .mapToObj(index -> new DiagnosisCreateRequest.JobRequest(
                        "회사 " + index,
                        "Backend Engineer",
                        "공고 내용 " + index
                ))
                .toList();

        return new DiagnosisCreateRequest(jobs);
    }

    private User createUser(Long id, String email) {
        User user = new User(email, "hashed-password", "문석현", null);
        ReflectionTestUtils.setField(user, "id", id);
        return user;
    }

    private Profile createProfile(Long id, User user) {
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ReflectionTestUtils.setField(profile, "id", id);
        return profile;
    }

    private Diagnosis createDiagnosis(Long id, Profile profile) {
        Diagnosis diagnosis = new Diagnosis(profile);
        ReflectionTestUtils.setField(diagnosis, "id", id);
        return diagnosis;
    }

    private JDResult createJdResult(Long id, Diagnosis diagnosis) {
        JDResult jdResult = new JDResult(
                diagnosis,
                "회사 A",
                "Backend Engineer",
                "공고 내용",
                1
        );
        ReflectionTestUtils.setField(jdResult, "id", id);
        return jdResult;
    }
}
