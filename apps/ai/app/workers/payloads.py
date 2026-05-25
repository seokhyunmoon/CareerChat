from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.pipeline.context import AnalysisPipelineContext
from app.schemas.analysis_job import AnalysisJobPosting, AnalysisJobRequest, CallbackTarget
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


class AnalysisTaskPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosisId: int = Field(ge=1)
    taskId: str = Field(min_length=1)
    callback: CallbackTarget
    profileSnapshot: ProfileSnapshot
    jobs: list[AnalysisJobPosting] = Field(min_length=1, max_length=3)
    metadata: AnalysisMetadata

    @classmethod
    def from_request(
        cls,
        *,
        request: AnalysisJobRequest,
        task_id: str,
        metadata: AnalysisMetadata,
    ) -> AnalysisTaskPayload:
        return cls(
            diagnosisId=request.diagnosisId,
            taskId=task_id,
            callback=request.callback,
            profileSnapshot=request.profileSnapshot,
            jobs=request.jobs,
            metadata=metadata,
        )

    def to_pipeline_context(self) -> AnalysisPipelineContext:
        return AnalysisPipelineContext(
            diagnosisId=self.diagnosisId,
            taskId=self.taskId,
            profileSnapshot=self.profileSnapshot,
            jobs=self.jobs,
            metadata=self.metadata,
        )
