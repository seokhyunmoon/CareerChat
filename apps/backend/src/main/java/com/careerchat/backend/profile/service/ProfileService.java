package com.careerchat.backend.profile.service;

import com.careerchat.backend.global.exception.BusinessException;
import com.careerchat.backend.global.exception.ErrorCode;
import com.careerchat.backend.profile.domain.Achievement;
import com.careerchat.backend.profile.domain.Education;
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
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProfileService {

    private final UserRepository userRepository;
    private final ProfileRepository profileRepository;
    private final EducationRepository educationRepository;
    private final WorkExperienceRepository workExperienceRepository;
    private final ProjectRepository projectRepository;
    private final AchievementRepository achievementRepository;

    public ProfileService(
            UserRepository userRepository,
            ProfileRepository profileRepository,
            EducationRepository educationRepository,
            WorkExperienceRepository workExperienceRepository,
            ProjectRepository projectRepository,
            AchievementRepository achievementRepository
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.educationRepository = educationRepository;
        this.workExperienceRepository = workExperienceRepository;
        this.projectRepository = projectRepository;
        this.achievementRepository = achievementRepository;
    }

    @Transactional(readOnly = true)
    public ProfileResponse getProfile(Long userId) {
        User user = getCurrentUser(userId);
        Profile profile = profileRepository.findByUser(user)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROFILE_NOT_FOUND));

        return toResponse(profile);
    }

    @Transactional
    public ProfileResponse saveProfile(Long userId, ProfileRequest request) {
        validateWorkOrProjectExists(request);

        User user = getCurrentUser(userId);
        Profile profile = profileRepository.findByUser(user)
                .map(existingProfile -> {
                    existingProfile.updateExperienceLevel(request.experienceLevel());
                    return existingProfile;
                })
                .orElseGet(() -> profileRepository.save(new Profile(user, request.experienceLevel())));

        deleteProfileDetails(profile);

        List<Education> education = saveEducation(profile, request.education());
        List<WorkExperience> workExperiences = saveWorkExperiences(profile, emptyIfNull(request.workExperiences()));
        List<Project> projects = saveProjects(profile, emptyIfNull(request.projects()));
        List<Achievement> achievements = saveAchievements(profile, emptyIfNull(request.achievements()));

        return ProfileResponse.of(profile, education, workExperiences, projects, achievements);
    }

    private User getCurrentUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "Authentication is required."));
    }

    private ProfileResponse toResponse(Profile profile) {
        return ProfileResponse.of(
                profile,
                educationRepository.findAllByProfileOrderByIdAsc(profile),
                workExperienceRepository.findAllByProfileOrderByIdAsc(profile),
                projectRepository.findAllByProfileOrderByIdAsc(profile),
                achievementRepository.findAllByProfileOrderByIdAsc(profile)
        );
    }

    private void validateWorkOrProjectExists(ProfileRequest request) {
        boolean hasWorkExperience = !emptyIfNull(request.workExperiences()).isEmpty();
        boolean hasProject = !emptyIfNull(request.projects()).isEmpty();

        if (!hasWorkExperience && !hasProject) {
            throw new BusinessException(
                    ErrorCode.INVALID_INPUT,
                    "At least one work experience or project is required."
            );
        }
    }

    private void deleteProfileDetails(Profile profile) {
        achievementRepository.deleteAllByProfile(profile);
        projectRepository.deleteAllByProfile(profile);
        workExperienceRepository.deleteAllByProfile(profile);
        educationRepository.deleteAllByProfile(profile);
    }

    private List<Education> saveEducation(Profile profile, List<ProfileRequest.EducationRequest> requests) {
        List<Education> education = requests.stream()
                .map(request -> new Education(
                        profile,
                        request.schoolName(),
                        request.gradStatus(),
                        request.degree(),
                        request.major(),
                        request.startDate(),
                        request.endDate()
                ))
                .toList();

        return educationRepository.saveAll(education);
    }

    private List<WorkExperience> saveWorkExperiences(
            Profile profile,
            List<ProfileRequest.WorkExperienceRequest> requests
    ) {
        List<WorkExperience> workExperiences = requests.stream()
                .map(request -> new WorkExperience(
                        profile,
                        request.companyName(),
                        request.employmentType(),
                        request.position(),
                        request.startDate(),
                        request.endDate(),
                        request.description()
                ))
                .toList();

        return workExperienceRepository.saveAll(workExperiences);
    }

    private List<Project> saveProjects(Profile profile, List<ProfileRequest.ProjectRequest> requests) {
        List<Project> projects = requests.stream()
                .map(request -> new Project(
                        profile,
                        request.projectName(),
                        request.description()
                ))
                .toList();

        return projectRepository.saveAll(projects);
    }

    private List<Achievement> saveAchievements(Profile profile, List<ProfileRequest.AchievementRequest> requests) {
        List<Achievement> achievements = requests.stream()
                .map(request -> new Achievement(
                        profile,
                        request.title(),
                        request.issuer(),
                        request.scoreOrGrade(),
                        request.acquiredDate()
                ))
                .toList();

        return achievementRepository.saveAll(achievements);
    }

    private static <T> List<T> emptyIfNull(List<T> values) {
        if (values == null) {
            return List.of();
        }

        return values;
    }
}
