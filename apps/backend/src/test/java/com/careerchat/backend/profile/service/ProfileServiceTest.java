package com.careerchat.backend.profile.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.Achievement;
import com.careerchat.backend.profile.domain.Education;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.domain.Project;
import com.careerchat.backend.profile.domain.WorkExperience;
import com.careerchat.backend.profile.dto.ProfileRequest;
import com.careerchat.backend.profile.dto.ProfileResponse;
import com.careerchat.backend.profile.repository.AchievementRepository;
import com.careerchat.backend.profile.repository.EducationRepository;
import com.careerchat.backend.profile.repository.ProfileRepository;
import com.careerchat.backend.profile.repository.ProjectRepository;
import com.careerchat.backend.profile.repository.WorkExperienceRepository;
import com.careerchat.backend.user.domain.User;
import com.careerchat.backend.user.repository.UserRepository;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ProfileServiceTest {

    private UserRepository userRepository;
    private ProfileRepository profileRepository;
    private EducationRepository educationRepository;
    private WorkExperienceRepository workExperienceRepository;
    private ProjectRepository projectRepository;
    private AchievementRepository achievementRepository;
    private ProfileService profileService;

    @BeforeEach
    void setUp() {
        userRepository = mock(UserRepository.class);
        profileRepository = mock(ProfileRepository.class);
        educationRepository = mock(EducationRepository.class);
        workExperienceRepository = mock(WorkExperienceRepository.class);
        projectRepository = mock(ProjectRepository.class);
        achievementRepository = mock(AchievementRepository.class);
        profileService = new ProfileService(
                userRepository,
                profileRepository,
                educationRepository,
                workExperienceRepository,
                projectRepository,
                achievementRepository
        );
    }

    @Test
    void getProfileReturnsCurrentUserProfile() {
        User user = new User("user@example.com", "hashed-password", "Moon", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        Education education = new Education(
                profile,
                "Yonsei University",
                "EXPECTED",
                "Bachelor",
                "Applied Information Engineering",
                LocalDate.of(2019, 9, 1),
                null
        );
        Project project = new Project(profile, "CareerChat", "Career analysis service.");

        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));
        when(educationRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(education));
        when(workExperienceRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of());
        when(projectRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(project));
        when(achievementRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of());

        ProfileResponse response = profileService.getProfile(1L);

        assertThat(response.experienceLevel()).isEqualTo(ExperienceLevel.NEW);
        assertThat(response.education()).hasSize(1);
        assertThat(response.education().getFirst().schoolName()).isEqualTo("Yonsei University");
        assertThat(response.projects()).hasSize(1);
        assertThat(response.projects().getFirst().projectName()).isEqualTo("CareerChat");
    }

    @Test
    void getProfileThrowsProfileNotFoundWhenProfileDoesNotExist() {
        User user = new User("user@example.com", "hashed-password", "Moon", null);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> profileService.getProfile(1L))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Profile not found.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.PROFILE_NOT_FOUND);
    }

    @Test
    void saveProfileCreatesProfileAndDetailsWhenProfileDoesNotExist() {
        User user = new User("user@example.com", "hashed-password", "Moon", null);
        ProfileRequest request = createProfileRequest(ExperienceLevel.NEW);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.empty());
        when(profileRepository.save(any(Profile.class))).thenAnswer(invocation -> invocation.getArgument(0));
        mockSaveAllRepositories();

        ProfileResponse response = profileService.saveProfile(1L, request);

        assertThat(response.experienceLevel()).isEqualTo(ExperienceLevel.NEW);
        assertThat(response.education()).hasSize(1);
        assertThat(response.workExperiences()).hasSize(1);
        assertThat(response.projects()).hasSize(1);
        assertThat(response.achievements()).hasSize(1);
        verify(profileRepository).save(any(Profile.class));
    }

    @Test
    void saveProfileUpdatesExistingProfileAndReplacesDetails() {
        User user = new User("user@example.com", "hashed-password", "Moon", null);
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ProfileRequest request = createProfileRequest(ExperienceLevel.EXPERIENCED);
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        when(profileRepository.findByUser(user)).thenReturn(Optional.of(profile));
        mockSaveAllRepositories();

        ProfileResponse response = profileService.saveProfile(1L, request);

        assertThat(response.experienceLevel()).isEqualTo(ExperienceLevel.EXPERIENCED);
        verify(achievementRepository).deleteAllByProfile(profile);
        verify(projectRepository).deleteAllByProfile(profile);
        verify(workExperienceRepository).deleteAllByProfile(profile);
        verify(educationRepository).deleteAllByProfile(profile);
        verify(profileRepository, never()).save(any(Profile.class));
    }

    @Test
    void saveProfileThrowsInvalidInputWhenWorkExperienceAndProjectAreMissing() {
        ProfileRequest request = new ProfileRequest(
                ExperienceLevel.NEW,
                List.of(new ProfileRequest.EducationRequest(
                        "Yonsei University",
                        "EXPECTED",
                        "Bachelor",
                        "Applied Information Engineering",
                        LocalDate.of(2019, 9, 1),
                        null
                )),
                List.of(),
                List.of(),
                List.of()
        );

        assertThatThrownBy(() -> profileService.saveProfile(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("At least one work experience or project is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.INVALID_INPUT);
    }

    @Test
    void saveProfileThrowsUnauthorizedWhenUserDoesNotExist() {
        ProfileRequest request = createProfileRequest(ExperienceLevel.NEW);
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> profileService.saveProfile(1L, request))
                .isInstanceOf(BusinessException.class)
                .hasMessage("Authentication is required.")
                .extracting("errorCode")
                .isEqualTo(ErrorCode.UNAUTHORIZED);
    }

    private void mockSaveAllRepositories() {
        when(educationRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));
        when(workExperienceRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));
        when(projectRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));
        when(achievementRepository.saveAll(any())).thenAnswer(invocation -> invocation.getArgument(0));
    }

    private ProfileRequest createProfileRequest(ExperienceLevel experienceLevel) {
        return new ProfileRequest(
                experienceLevel,
                List.of(new ProfileRequest.EducationRequest(
                        "Yonsei University",
                        "EXPECTED",
                        "Bachelor",
                        "Applied Information Engineering",
                        LocalDate.of(2019, 9, 1),
                        null
                )),
                List.of(new ProfileRequest.WorkExperienceRequest(
                        "A*STAR IHPC",
                        "INTERN",
                        "Research Intern",
                        LocalDate.of(2025, 9, 1),
                        LocalDate.of(2025, 12, 1),
                        "AI research internship."
                )),
                List.of(new ProfileRequest.ProjectRequest(
                        "CareerChat",
                        "Career analysis service."
                )),
                List.of(new ProfileRequest.AchievementRequest(
                        "OPIc IH",
                        "ACTFL",
                        "IH",
                        LocalDate.of(2025, 3, 1)
                ))
        );
    }
}
