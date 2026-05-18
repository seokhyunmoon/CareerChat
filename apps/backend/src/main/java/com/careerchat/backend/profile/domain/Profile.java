package com.careerchat.backend.profile.domain;

import com.careerchat.backend.global.common.BaseTimeEntity;
import com.careerchat.backend.user.domain.User;
import jakarta.persistence.*;

import java.util.Objects;

@Entity
@Table(
    name = "profiles",
    uniqueConstraints = {
        @UniqueConstraint(name = "uk_profiles_user", columnNames = "user_id")
    }
)

public class Profile extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "profile_id")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
        name = "user_id",
        nullable = false,
        foreignKey = @ForeignKey(name = "fk_profiles_user")
    )
    private User user;

    @Enumerated(EnumType.STRING)
    @Column(name = "experience_level", nullable = false, length = 20)
    private ExperienceLevel experienceLevel;

    protected Profile() {
    }

    public Profile(User user, ExperienceLevel experienceLevel) {
        this.user = Objects.requireNonNull(user);
        this.experienceLevel = Objects.requireNonNull(experienceLevel);
    }

    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public ExperienceLevel getExperienceLevel() {
        return experienceLevel;
    }
}
