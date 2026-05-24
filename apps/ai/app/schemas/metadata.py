from __future__ import annotations

from pydantic import BaseModel, Field


class AnalysisStepMetadata(BaseModel):
    step: str
    modelName: str | None = None
    promptVersion: str | None = None
    durationMs: int | None = None
    retryCount: int | None = None


class AnalysisMetadata(BaseModel):
    pipelineVersion: str
    promptSetVersion: str
    defaultModel: str | None = None
    retrievalTopK: int | None = None
    steps: dict[str, AnalysisStepMetadata] = Field(default_factory=dict)


class ErrorDetails(BaseModel):
    retryable: bool
    provider: str | None = None
    model: str | None = None
    taskId: str | None = None
    traceId: str | None = None
