package com.careerchat.backend.ai.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

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
import com.careerchat.backend.user.domain.User;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class ProfileSnapshotFactoryTest {

    private EducationRepository educationRepository;
    private WorkExperienceRepository workExperienceRepository;
    private ProjectRepository projectRepository;
    private AchievementRepository achievementRepository;
    private ProfileSnapshotFactory factory;

    @BeforeEach
    void setUp() {
        educationRepository = mock(EducationRepository.class);
        workExperienceRepository = mock(WorkExperienceRepository.class);
        projectRepository = mock(ProjectRepository.class);
        achievementRepository = mock(AchievementRepository.class);
        factory = new ProfileSnapshotFactory(
                educationRepository,
                workExperienceRepository,
                projectRepository,
                achievementRepository
        );
    }

    @Test
    void createBuildsProfileSnapshotWithoutUserPii() {
        User user = new User("user@example.com", "hashed-password", "문석현", "010-0000-0000");
        Profile profile = new Profile(user, ExperienceLevel.NEW);
        ReflectionTestUtils.setField(profile, "id", 10L);

        Education education = new Education(
                profile,
                "Yonsei University",
                "GRADUATED",
                "Bachelor",
                "Computer Science",
                LocalDate.of(2020, 3, 1),
                LocalDate.of(2024, 2, 28)
        );
        ReflectionTestUtils.setField(education, "id", 20L);
        WorkExperience workExperience = new WorkExperience(
                profile,
                "회사 A",
                "FULL_TIME",
                "Backend Engineer",
                LocalDate.of(2024, 3, 1),
                null,
                "Spring API 개발"
        );
        ReflectionTestUtils.setField(workExperience, "id", 30L);
        Project project = new Project(profile, "CareerChat", "AI 공고 매칭 서비스");
        ReflectionTestUtils.setField(project, "id", 40L);
        Achievement achievement = new Achievement(
                profile,
                "정보처리기사",
                "한국산업인력공단",
                "PASS",
                LocalDate.of(2024, 6, 1)
        );
        ReflectionTestUtils.setField(achievement, "id", 50L);

        when(educationRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(education));
        when(workExperienceRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(workExperience));
        when(projectRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(project));
        when(achievementRepository.findAllByProfileOrderByIdAsc(profile)).thenReturn(List.of(achievement));

        AiProfileSnapshot snapshot = factory.create(profile);

        assertThat(snapshot.snapshotVersion()).isEqualTo(1);
        assertThat(snapshot.profile().profileId()).isEqualTo(10L);
        assertThat(snapshot.profile().experienceLevel()).isEqualTo("NEW");
        assertThat(snapshot.education().getFirst().educationId()).isEqualTo(20L);
        assertThat(snapshot.workExperiences().getFirst().workExperienceId()).isEqualTo(30L);
        assertThat(snapshot.projects().getFirst().projectId()).isEqualTo(40L);
        assertThat(snapshot.achievements().getFirst().achievementId()).isEqualTo(50L);
    }
}
