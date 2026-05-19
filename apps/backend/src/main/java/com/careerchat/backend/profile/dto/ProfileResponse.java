package com.careerchat.backend.profile.dto;

import com.careerchat.backend.profile.domain.Achievement;
import com.careerchat.backend.profile.domain.Education;
import com.careerchat.backend.profile.domain.ExperienceLevel;
import com.careerchat.backend.profile.domain.Profile;
import com.careerchat.backend.profile.domain.Project;
import com.careerchat.backend.profile.domain.WorkExperience;
import java.time.LocalDate;
import java.util.List;

public record ProfileResponse(
        Long profileId,
        ExperienceLevel experienceLevel,
        List<EducationResponse> education,
        List<WorkExperienceResponse> workExperiences,
        List<ProjectResponse> projects,
        List<AchievementResponse> achievements
) {

    public static ProfileResponse of(
            Profile profile,
            List<Education> education,
            List<WorkExperience> workExperiences,
            List<Project> projects,
            List<Achievement> achievements
    ) {
        return new ProfileResponse(
                profile.getId(),
                profile.getExperienceLevel(),
                education.stream().map(EducationResponse::from).toList(),
                workExperiences.stream().map(WorkExperienceResponse::from).toList(),
                projects.stream().map(ProjectResponse::from).toList(),
                achievements.stream().map(AchievementResponse::from).toList()
        );
    }

    public record EducationResponse(
            Long educationId,
            String schoolName,
            String gradStatus,
            String degree,
            String major,
            LocalDate startDate,
            LocalDate endDate
    ) {

        static EducationResponse from(Education education) {
            return new EducationResponse(
                    education.getId(),
                    education.getSchoolName(),
                    education.getGradStatus(),
                    education.getDegree(),
                    education.getMajor(),
                    education.getStartDate(),
                    education.getEndDate()
            );
        }
    }

    public record WorkExperienceResponse(
            Long workExperienceId,
            String companyName,
            String employmentType,
            String position,
            LocalDate startDate,
            LocalDate endDate,
            String description
    ) {

        static WorkExperienceResponse from(WorkExperience workExperience) {
            return new WorkExperienceResponse(
                    workExperience.getId(),
                    workExperience.getCompanyName(),
                    workExperience.getEmploymentType(),
                    workExperience.getPosition(),
                    workExperience.getStartDate(),
                    workExperience.getEndDate(),
                    workExperience.getDescription()
            );
        }
    }

    public record ProjectResponse(
            Long projectId,
            String projectName,
            String description
    ) {

        static ProjectResponse from(Project project) {
            return new ProjectResponse(
                    project.getId(),
                    project.getProjectName(),
                    project.getDescription()
            );
        }
    }

    public record AchievementResponse(
            Long achievementId,
            String title,
            String issuer,
            String scoreOrGrade,
            LocalDate acquiredDate
    ) {

        static AchievementResponse from(Achievement achievement) {
            return new AchievementResponse(
                    achievement.getId(),
                    achievement.getTitle(),
                    achievement.getIssuer(),
                    achievement.getScoreOrGrade(),
                    achievement.getAcquiredDate()
            );
        }
    }
}
