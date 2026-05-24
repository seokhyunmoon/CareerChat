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
    taskId: str
    reportSummary: str
    reportContent: str
    completedAt: datetime
    modelName: str | None = None
    promptVersion: str | None = None
    analysisMetadata: str | None = None
    jobs: list[CompleteCallbackJobResult]


class FailCallbackPayload(BaseModel):
    taskId: str
    errorCode: str | None = None
    errorMessage: str
    failedStep: str | None = None
    failedAt: datetime
    errorDetails: str | None = None
