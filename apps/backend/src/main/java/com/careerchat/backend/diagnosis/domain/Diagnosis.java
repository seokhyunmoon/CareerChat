package com.careerchat.backend.diagnosis.domain;

import com.careerchat.backend.global.common.BaseTimeEntity;
import com.careerchat.backend.profile.domain.Profile;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.ForeignKey;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import java.util.Objects;

@Entity
@Table(name = "diagnoses")
public class Diagnosis extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "diagnosis_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "profile_id",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_diagnoses_profile")
    )
    private Profile profile;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 30)
    private DiagnosisStatus status;

    @Column(name = "report_summary", columnDefinition = "TEXT")
    private String reportSummary;

    @Column(name = "report_content", columnDefinition = "TEXT")
    private String reportContent;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    protected Diagnosis() {
    }

    public Diagnosis(Profile profile) {
        this.profile = Objects.requireNonNull(profile);
        this.status = DiagnosisStatus.PENDING;
    }

    public Long getId() {
        return id;
    }

    public Profile getProfile() {
        return profile;
    }

    public DiagnosisStatus getStatus() {
        return status;
    }

    public String getReportSummary() {
        return reportSummary;
    }

    public String getReportContent() {
        return reportContent;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public LocalDateTime getCompletedAt() {
        return completedAt;
    }

    public void markProcessing() {
        this.status = DiagnosisStatus.PROCESSING;
    }

    public void complete(String reportSummary, String reportContent, LocalDateTime completedAt) {
        this.status = DiagnosisStatus.COMPLETED;
        this.reportSummary = reportSummary;
        this.reportContent = reportContent;
        this.errorMessage = null;
        this.completedAt = Objects.requireNonNull(completedAt);
    }

    public void fail(String errorMessage, LocalDateTime completedAt) {
        this.status = DiagnosisStatus.FAILED;
        this.errorMessage = Objects.requireNonNull(errorMessage);
        this.completedAt = Objects.requireNonNull(completedAt);
    }
}
