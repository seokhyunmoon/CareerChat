from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ChatMessageRole = Literal["USER", "ASSISTANT"]


class ResultChatJobResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jdId: int = Field(ge=1)
    rankOrder: int | None = Field(default=None, ge=1, le=3)
    companyName: str = Field(min_length=1, max_length=255)
    position: str | None = Field(default=None, max_length=255)
    fitScore: float | None = Field(default=None, ge=0, le=100)
    strengthsSummary: str | None = None
    gapsSummary: str | None = None
    highlightPoints: list[str] = Field(default_factory=list)
    matchDetails: list[dict[str, Any]] = Field(default_factory=list)


class PreviousChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: ChatMessageRole
    content: str = Field(min_length=1, max_length=4000)


class ResultChatResponseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosisId: int = Field(ge=1)
    userMessage: str = Field(min_length=1, max_length=2000)
    reportSummary: str = Field(min_length=1)
    reportContent: str = Field(min_length=1)
    jobResults: list[ResultChatJobResult] = Field(min_length=1, max_length=3)
    previousMessages: list[PreviousChatMessage] = Field(default_factory=list, max_length=20)

    @field_validator("jobResults")
    @classmethod
    def validate_unique_job_results(
        cls,
        job_results: list[ResultChatJobResult],
    ) -> list[ResultChatJobResult]:
        jd_ids = [job.jdId for job in job_results]
        if len(jd_ids) != len(set(jd_ids)):
            raise ValueError("jobResults must not contain duplicate jdId values")

        rank_orders = [
            job.rankOrder
            for job in job_results
            if job.rankOrder is not None
        ]
        if len(rank_orders) != len(set(rank_orders)):
            raise ValueError("jobResults must not contain duplicate rankOrder values")

        return job_results


class ResultChatEvidenceData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    referencedJobIds: list[int] = Field(default_factory=list)
    reasonCodes: list[str] = Field(default_factory=list)
    usedFields: list[str] = Field(default_factory=list)

    @field_validator("referencedJobIds")
    @classmethod
    def validate_unique_referenced_job_ids(cls, jd_ids: list[int]) -> list[int]:
        if any(jd_id < 1 for jd_id in jd_ids):
            raise ValueError("referencedJobIds must contain positive jdId values")
        if len(jd_ids) != len(set(jd_ids)):
            raise ValueError("referencedJobIds must not contain duplicate values")
        return jd_ids


class ResultChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1)
    evidenceData: ResultChatEvidenceData
    providerName: str = Field(min_length=1)
    modelName: str = Field(min_length=1)
    promptKey: str = Field(min_length=1)
    promptVersion: str = Field(min_length=1)
