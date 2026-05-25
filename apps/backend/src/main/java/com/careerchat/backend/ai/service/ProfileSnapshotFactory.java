package com.careerchat.backend.ai.service;

import com.careerchat.backend.ai.dto.AiProfileSnapshot;
import com.careerchat.backend.profile.domain.Achievement;
import com.careerchat.backend.profile.domain.Education;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.domain.Project;
import com.careerchat.backend.profile.domain.WorkExperience;
import com.careerchat.backend.profile.repository.AchievementRepository;
import com.careerchat.backend.profile.repository.EducationRepository;
import com.careerchat.backend.profile.repository.ProjectRepository;
import com.careerchat.backend.profile.repository.WorkExperienceRepository;
import org.springframework.stereotype.Component;

@Component
public class ProfileSnapshotFactory {

    private static final int SNAPSHOT_VERSION = 1;

    private final EducationRepository educationRepository;
    private final WorkExperienceRepository workExperienceRepository;
    private final ProjectRepository projectRepository;
    private final AchievementRepository achievementRepository;

    public ProfileSnapshotFactory(
            EducationRepository educationRepository,
            WorkExperienceRepository workExperienceRepository,
            ProjectRepository projectRepository,
            AchievementRepository achievementRepository
    ) {
        this.educationRepository = educationRepository;
        this.workExperienceRepository = workExperienceRepository;
        this.projectRepository = projectRepository;
        this.achievementRepository = achievementRepository;
    }

    public AiProfileSnapshot create(Profile profile) {
        return new AiProfileSnapshot(
                SNAPSHOT_VERSION,
                new AiProfileSnapshot.SnapshotProfile(
                        profile.getId(),
                        experienceLevelName(profile.getExperienceLevel())
                ),
                educationRepository.findAllByProfileOrderByIdAsc(profile).stream()
                        .map(this::toEducationSnapshot)
                        .toList(),
                workExperienceRepository.findAllByProfileOrderByIdAsc(profile).stream()
                        .map(this::toWorkExperienceSnapshot)
                        .toList(),
                projectRepository.findAllByProfileOrderByIdAsc(profile).stream()
                        .map(this::toProjectSnapshot)
                        .toList(),
                achievementRepository.findAllByProfileOrderByIdAsc(profile).stream()
                        .map(this::toAchievementSnapshot)
                        .toList()
        );
    }

    private AiProfileSnapshot.EducationSnapshot toEducationSnapshot(Education education) {
        return new AiProfileSnapshot.EducationSnapshot(
                education.getId(),
                education.getSchoolName(),
                education.getGradStatus(),
                education.getDegree(),
                education.getMajor(),
                education.getStartDate(),
                education.getEndDate()
        );
    }

    private AiProfileSnapshot.WorkExperienceSnapshot toWorkExperienceSnapshot(WorkExperience workExperience) {
        return new AiProfileSnapshot.WorkExperienceSnapshot(
                workExperience.getId(),
                workExperience.getCompanyName(),
                workExperience.getEmploymentType(),
                workExperience.getPosition(),
                workExperience.getStartDate(),
                workExperience.getEndDate(),
                workExperience.getDescription()
        );
    }

    private AiProfileSnapshot.ProjectSnapshot toProjectSnapshot(Project project) {
        return new AiProfileSnapshot.ProjectSnapshot(
                project.getId(),
                project.getProjectName(),
                project.getDescription()
        );
    }

    private AiProfileSnapshot.AchievementSnapshot toAchievementSnapshot(Achievement achievement) {
        return new AiProfileSnapshot.AchievementSnapshot(
                achievement.getId(),
                achievement.getTitle(),
                achievement.getIssuer(),
                achievement.getScoreOrGrade(),
                achievement.getAcquiredDate()
        );
    }

    private String experienceLevelName(ExperienceLevel experienceLevel) {
        if (experienceLevel == null) {
            return null;
        }

        return experienceLevel.name();
    }
}
