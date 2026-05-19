package com.careerchat.backend.profile.dto;

import com.careerchat.backend.profile.domain.ExperienceLevel;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.List;

public record ProfileRequest(

        @NotNull(message = "Experience level is required.")
        ExperienceLevel experienceLevel,

        @NotEmpty(message = "Education is required.")
        @Valid
        List<EducationRequest> education,

        @Valid
        List<WorkExperienceRequest> workExperiences,

        @Valid
        List<ProjectRequest> projects,

        @Valid
        List<AchievementRequest> achievements
) {

    public record EducationRequest(

            @NotBlank(message = "School name is required.")
            @Size(max = 255, message = "School name must be 255 characters or less.")
            String schoolName,

            @NotBlank(message = "Graduation status is required.")
            @Size(max = 30, message = "Graduation status must be 30 characters or less.")
            String gradStatus,

            @Size(max = 100, message = "Degree must be 100 characters or less.")
            String degree,

            @Size(max = 255, message = "Major must be 255 characters or less.")
            String major,

            LocalDate startDate,

            LocalDate endDate
    ) {
    }

    public record WorkExperienceRequest(

            @NotBlank(message = "Company name is required.")
            @Size(max = 255, message = "Company name must be 255 characters or less.")
            String companyName,

            @NotBlank(message = "Employment type is required.")
            @Size(max = 50, message = "Employment type must be 50 characters or less.")
            String employmentType,

            @Size(max = 255, message = "Position must be 255 characters or less.")
            String position,

            LocalDate startDate,

            LocalDate endDate,

            String description
    ) {
    }

    public record ProjectRequest(

            @NotBlank(message = "Project name is required.")
            @Size(max = 255, message = "Project name must be 255 characters or less.")
            String projectName,

            @NotBlank(message = "Project description is required.")
            String description
    ) {
    }

    public record AchievementRequest(

            @NotBlank(message = "Achievement title is required.")
            @Size(max = 255, message = "Achievement title must be 255 characters or less.")
            String title,

            @Size(max = 255, message = "Issuer must be 255 characters or less.")
            String issuer,

            @Size(max = 100, message = "Score or grade must be 100 characters or less.")
            String scoreOrGrade,

            LocalDate acquiredDate
    ) {
    }
}
