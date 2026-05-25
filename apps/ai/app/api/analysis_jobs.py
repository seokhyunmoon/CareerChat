from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, status

from app.prompts.manifest import (
    DEFAULT_MODEL_NAME,
    DEFAULT_PIPELINE_VERSION,
    DEFAULT_PROMPT_SET_VERSION,
)
from app.schemas.analysis_job import AnalysisJobCreateResponse, AnalysisJobRequest
from app.schemas.metadata import AnalysisMetadata
from app.workers.payloads import AnalysisTaskPayload
from app.workers.tasks import enqueue_analysis_task

router = APIRouter(prefix="/analysis/jobs", tags=["analysis-jobs"])


@router.post("", response_model=AnalysisJobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_analysis_job(request: AnalysisJobRequest) -> AnalysisJobCreateResponse:
    task_id = str(uuid4())
    metadata = AnalysisMetadata(
        pipelineVersion=DEFAULT_PIPELINE_VERSION,
        promptSetVersion=DEFAULT_PROMPT_SET_VERSION,
        defaultModel=DEFAULT_MODEL_NAME,
    )
    payload = AnalysisTaskPayload.from_request(
        request=request,
        task_id=task_id,
        metadata=metadata,
    )
    enqueue_analysis_task(payload)

    return AnalysisJobCreateResponse(
        diagnosisId=request.diagnosisId,
        taskId=task_id,
        status="QUEUED",
    )
