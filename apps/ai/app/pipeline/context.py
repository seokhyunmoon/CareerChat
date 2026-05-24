from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


class AnalysisPipelineContext(BaseModel):
    diagnosisId: int
    taskId: str
    profileSnapshot: ProfileSnapshot
    jobs: list[AnalysisJobPosting] = Field(min_length=1, max_length=3)
    metadata: AnalysisMetadata


class AnalysisPipelineResult(BaseModel):
    diagnosisId: int
    taskId: str
    metadata: AnalysisMetadata
