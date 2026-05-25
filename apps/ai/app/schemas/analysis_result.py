from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.schemas.profile_snapshot import ProfileEvidenceReference

RequirementCategory = Literal[
    "skill",
    "experience",
    "qualification",
    "responsibility",
    "preference",
    "other",
]
RequirementPriority = Literal["required", "preferred", "optional"]
RequirementMatchStatus = Literal["matched", "partial", "missing"]


class JobRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirementId: str = Field(min_length=1)
    category: RequirementCategory = "other"
    priority: RequirementPriority = "required"
    description: str = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)
    sourceText: str | None = None


class MatchedProfileEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence: ProfileEvidenceReference
    relevanceScore: float = Field(ge=0, le=1)
    rationale: str | None = None


class RequirementMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement: JobRequirement
    status: RequirementMatchStatus
    confidenceScore: float = Field(ge=0, le=1)
    evidence: list[MatchedProfileEvidence] = Field(default_factory=list)
    rationale: str | None = None
    gap: str | None = None

    @field_validator("evidence")
    @classmethod
    def validate_missing_match_has_no_evidence(
        cls,
        evidence: list[MatchedProfileEvidence],
        info: ValidationInfo,
    ) -> list[MatchedProfileEvidence]:
        if info.data.get("status") == "missing" and evidence:
            raise ValueError("missing requirement matches must not contain evidence")

        return evidence


class JobAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jdId: int = Field(ge=1)
    rankOrder: int = Field(ge=1, le=3)
    companyName: str = Field(min_length=1, max_length=255)
    position: str | None = Field(default=None, max_length=255)
    fitScore: float = Field(ge=0, le=100)
    strengthsSummary: str | None = None
    gapsSummary: str | None = None
    highlightPoints: list[str] = Field(default_factory=list)
    requirementMatches: list[RequirementMatch] = Field(default_factory=list)


class AnalysisReportPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosisId: int = Field(ge=1)
    taskId: str = Field(min_length=1)
    reportSummary: str = Field(min_length=1)
    reportContent: str = Field(min_length=1)
    jobs: list[JobAnalysisResult] = Field(min_length=1, max_length=3)

    @field_validator("jobs")
    @classmethod
    def validate_unique_jobs_and_ranks(
        cls,
        jobs: list[JobAnalysisResult],
    ) -> list[JobAnalysisResult]:
        jd_ids = [job.jdId for job in jobs]
        if len(jd_ids) != len(set(jd_ids)):
            raise ValueError("jobs must not contain duplicate jdId values")

        rank_orders = [job.rankOrder for job in jobs]
        if len(rank_orders) != len(set(rank_orders)):
            raise ValueError("jobs must not contain duplicate rankOrder values")

        return jobs
