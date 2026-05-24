from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.schemas.profile_snapshot import ProfileSnapshot


class CallbackTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    completeUrl: HttpUrl
    failUrl: HttpUrl


class AnalysisJobPosting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jdId: int
    displayOrder: int = Field(ge=1, le=3)
    companyName: str = Field(min_length=1, max_length=255)
    position: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1)


class AnalysisJobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosisId: int
    callback: CallbackTarget
    profileSnapshot: ProfileSnapshot
    jobs: list[AnalysisJobPosting] = Field(min_length=1, max_length=3)

    @field_validator("jobs")
    @classmethod
    def validate_display_order(cls, jobs: list[AnalysisJobPosting]) -> list[AnalysisJobPosting]:
        display_orders = [job.displayOrder for job in jobs]
        if len(display_orders) != len(set(display_orders)):
            raise ValueError("jobs must not contain duplicate displayOrder values")

        return jobs


class AnalysisJobCreateResponse(BaseModel):
    diagnosisId: int
    taskId: str
    status: Literal["QUEUED"]
