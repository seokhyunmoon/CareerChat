package com.careerchat.backend.diagnosis.domain;

import com.careerchat.backend.global.common.BaseTimeEntity;
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
import jakarta.persistence.UniqueConstraint;
import java.math.BigDecimal;
import java.util.Objects;

@Entity
@Table(
        name = "jd_results",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_jd_results_diagnosis_display_order",
                        columnNames = {"diagnosis_id", "display_order"}
                ),
                @UniqueConstraint(
                        name = "uk_jd_results_diagnosis_rank_order",
                        columnNames = {"diagnosis_id", "rank_order"}
                )
        }
)
public class JDResult extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "jd_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "diagnosis_id",
            nullable = false,
            foreignKey = @ForeignKey(name = "fk_jd_results_diagnosis")
    )
    private Diagnosis diagnosis;

    @Column(name = "company_name", nullable = false, length = 255)
    private String companyName;

    @Column(name = "position", length = 255)
    private String position;

    @Column(name = "content", nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "display_order", nullable = false)
    private Integer displayOrder;

    @Column(name = "rank_order")
    private Integer rankOrder;

    @Column(name = "fit_score", precision = 5, scale = 2)
    private BigDecimal fitScore;

    @Column(name = "strengths_summary", columnDefinition = "TEXT")
    private String strengthsSummary;

    @Column(name = "gaps_summary", columnDefinition = "TEXT")
    private String gapsSummary;

    @Column(name = "highlight_points", columnDefinition = "TEXT")
    private String highlightPoints;

    protected JDResult() {
    }

    public JDResult(
            Diagnosis diagnosis,
            String companyName,
            String position,
            String content,
            Integer displayOrder
    ) {
        this.diagnosis = Objects.requireNonNull(diagnosis);
        this.companyName = Objects.requireNonNull(companyName);
        this.position = position;
        this.content = Objects.requireNonNull(content);
        this.displayOrder = Objects.requireNonNull(displayOrder);
    }

    public Long getId() {
        return id;
    }

    public Diagnosis getDiagnosis() {
        return diagnosis;
    }

    public String getCompanyName() {
        return companyName;
    }

    public String getPosition() {
        return position;
    }

    public String getContent() {
        return content;
    }

    public Integer getDisplayOrder() {
        return displayOrder;
    }

    public Integer getRankOrder() {
        return rankOrder;
    }

    public BigDecimal getFitScore() {
        return fitScore;
    }

    public String getStrengthsSummary() {
        return strengthsSummary;
    }

    public String getGapsSummary() {
        return gapsSummary;
    }

    public String getHighlightPoints() {
        return highlightPoints;
    }

    public void updateAnalysisResult(
            Integer rankOrder,
            BigDecimal fitScore,
            String strengthsSummary,
            String gapsSummary,
            String highlightPoints
    ) {
        this.rankOrder = rankOrder;
        this.fitScore = fitScore;
        this.strengthsSummary = strengthsSummary;
        this.gapsSummary = gapsSummary;
        this.highlightPoints = highlightPoints;
    }
}