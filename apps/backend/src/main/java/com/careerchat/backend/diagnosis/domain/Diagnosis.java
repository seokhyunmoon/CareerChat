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
import org.hibernate.annotations.ColumnTransformer;

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

    @Column(name = "profile_snapshot", columnDefinition = "jsonb")
    @ColumnTransformer(write = "?::jsonb")
    private String profileSnapshot;

    @Column(name = "ai_task_id", length = 255)
    private String aiTaskId;

    @Column(name = "analysis_started_at")
    private LocalDateTime analysisStartedAt;

    @Column(name = "model_name", length = 100)
    private String modelName;

    @Column(name = "prompt_version", length = 100)
    private String promptVersion;

    @Column(name = "analysis_metadata", columnDefinition = "jsonb")
    @ColumnTransformer(write = "?::jsonb")
    private String analysisMetadata;

    @Column(name = "report_summary", columnDefinition = "TEXT")
    private String reportSummary;

    @Column(name = "report_content", columnDefinition = "TEXT")
    private String reportContent;

    @Column(name = "error_code", length = 100)
    private String errorCode;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "failed_step", length = 100)
    private String failedStep;

    @Column(name = "failed_at")
    private LocalDateTime failedAt;

    @Column(name = "error_details", columnDefinition = "jsonb")
    @ColumnTransformer(write = "?::jsonb")
    private String errorDetails;

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

    public String getProfileSnapshot() {
        return profileSnapshot;
    }

    public String getAiTaskId() {
        return aiTaskId;
    }

    public LocalDateTime getAnalysisStartedAt() {
        return analysisStartedAt;
    }

    public String getModelName() {
        return modelName;
    }

    public String getPromptVersion() {
        return promptVersion;
    }

    public String getAnalysisMetadata() {
        return analysisMetadata;
    }

    public String getReportSummary() {
        return reportSummary;
    }

    public String getReportContent() {
        return reportContent;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public String getFailedStep() {
        return failedStep;
    }

    public LocalDateTime getFailedAt() {
        return failedAt;
    }

    public String getErrorDetails() {
        return errorDetails;
    }

    public LocalDateTime getCompletedAt() {
        return completedAt;
    }

    public void markProcessing() {
        this.status = DiagnosisStatus.PROCESSING;
    }

    public void startAnalysis(
            String aiTaskId,
            String profileSnapshot,
            LocalDateTime analysisStartedAt
    ) {
        this.status = DiagnosisStatus.PROCESSING;
        this.aiTaskId = Objects.requireNonNull(aiTaskId);
        this.profileSnapshot = profileSnapshot;
        this.analysisStartedAt = Objects.requireNonNull(analysisStartedAt);
        clearFailure();
    }

    public void updateAiMetadata(
            String modelName,
            String promptVersion,
            String analysisMetadata
    ) {
        this.modelName = modelName;
        this.promptVersion = promptVersion;
        this.analysisMetadata = analysisMetadata;
    }

    public void complete(String reportSummary, String reportContent, LocalDateTime completedAt) {
        this.status = DiagnosisStatus.COMPLETED;
        this.reportSummary = reportSummary;
        this.reportContent = reportContent;
        this.completedAt = Objects.requireNonNull(completedAt);
        clearFailure();
    }

    public void fail(String errorMessage, LocalDateTime completedAt) {
        fail(null, errorMessage, null, null, completedAt);
    }

    public void fail(
            String errorCode,
            String errorMessage,
            String failedStep,
            String errorDetails,
            LocalDateTime failedAt
    ) {
        this.status = DiagnosisStatus.FAILED;
        this.errorCode = errorCode;
        this.errorMessage = Objects.requireNonNull(errorMessage);
        this.failedStep = failedStep;
        this.errorDetails = errorDetails;
        this.failedAt = Objects.requireNonNull(failedAt);
        this.completedAt = this.failedAt;
    }

    private void clearFailure() {
        this.errorCode = null;
        this.errorMessage = null;
        this.failedStep = null;
        this.failedAt = null;
        this.errorDetails = null;
    }
}
