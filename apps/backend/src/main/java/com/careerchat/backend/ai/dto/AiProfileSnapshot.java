package com.careerchat.backend.ai.dto;

import java.time.LocalDate;
import java.util.List;

public record AiProfileSnapshot(
        int snapshotVersion,
        SnapshotProfile profile,
        List<EducationSnapshot> education,
        List<WorkExperienceSnapshot> workExperiences,
        List<ProjectSnapshot> projects,
        List<AchievementSnapshot> achievements
) {

    public record SnapshotProfile(
            Long profileId,
            String experienceLevel
    ) {
    }

    public record EducationSnapshot(
            Long educationId,
            String schoolName,
            String gradStatus,
            String degree,
            String major,
            LocalDate startDate,
            LocalDate endDate
    ) {
    }

    public record WorkExperienceSnapshot(
            Long workExperienceId,
            String companyName,
            String employmentType,
            String position,
            LocalDate startDate,
            LocalDate endDate,
            String description
    ) {
    }

    public record ProjectSnapshot(
            Long projectId,
            String projectName,
            String description
    ) {
    }

    public record AchievementSnapshot(
            Long achievementId,
            String title,
            String issuer,
            String scoreOrGrade,
            LocalDate acquiredDate
    ) {
    }
}
