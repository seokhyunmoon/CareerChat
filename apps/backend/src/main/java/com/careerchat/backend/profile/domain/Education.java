package com.careerchat.backend.profile.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDate;
import java.util.Objects;

@Entity
@Table(name = "education")
public class Education {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "edu_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
        name = "profile_id",
        nullable = false,
        foreignKey = @ForeignKey(name = "fk_education_profile")
    )
    private Profile profile;

    @Column(name = "school_name", nullable = false, length = 255)
    private String schoolName;

    @Column(name = "grad_status", nullable = false, length = 30)
    private String gradStatus;

    @Column(name = "degree", length = 100)
    private String degree;

    @Column(name = "major", length = 255)
    private String major;

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "end_date")
    private LocalDate endDate;

    protected Education() {
    }

    public Education(
        Profile profile,
        String schoolName,
        String gradStatus,
        String degree,
        String major,
        LocalDate startDate,
        LocalDate endDate
    ) {
        this.profile = Objects.requireNonNull(profile);
        this.schoolName = Objects.requireNonNull(schoolName);
        this.gradStatus = Objects.requireNonNull(gradStatus);
        this.degree = degree;
        this.major = major;
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public Long getId() {
        return id;
    }

    public Profile getProfile() {
        return profile;
    }

    public String getSchoolName() {
        return schoolName;
    }

    public String getGradStatus() {
        return gradStatus;
    }

    public String getDegree() {
        return degree;
    }

    public String getMajor() {
        return major;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }
}