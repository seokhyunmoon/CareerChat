from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CompleteCallbackJobResult(BaseModel):
    jdId: int
    rankOrder: int
    fitScore: float = Field(ge=0, le=100)
    strengthsSummary: str | None = None
    gapsSummary: str | None = None
    highlightPoints: str | None = None
    matchDetails: str | None = None


class CompleteCallbackPayload(BaseModel):
    taskId: str = Field(min_length=1)
    reportSummary: str = Field(min_length=1)
    reportContent: str = Field(min_length=1)
    completedAt: datetime
    modelName: str | None = Field(default=None, max_length=100)
    promptVersion: str | None = Field(default=None, max_length=100)
    analysisMetadata: str | None = None
    jobs: list[CompleteCallbackJobResult]


class FailCallbackPayload(BaseModel):
    taskId: str = Field(min_length=1)
    errorCode: str | None = Field(default=None, max_length=100)
    errorMessage: str = Field(min_length=1)
    failedStep: str | None = Field(default=None, max_length=100)
    failedAt: datetime
    errorDetails: str | None = None
