from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.pipeline.context import AnalysisPipelineContext
from app.schemas.analysis_job import AnalysisJobRequest
from app.schemas.metadata import AnalysisMetadata
from app.workers.payloads import AnalysisTaskPayload


def build_analysis_job_request() -> AnalysisJobRequest:
    return AnalysisJobRequest.model_validate(
        {
            "diagnosisId": 1,
            "callback": {
                "completeUrl": "http://localhost:8080/api/internal/ai/callback/complete",
                "failUrl": "http://localhost:8080/api/internal/ai/callback/fail",
            },
            "profileSnapshot": {
                "snapshotVersion": 1,
                "profile": {
                    "profileId": 1,
                    "experienceLevel": "JUNIOR",
                },
                "education": [],
                "workExperiences": [],
                "projects": [],
                "achievements": [],
            },
            "jobs": [
                {
                    "jdId": 1,
                    "displayOrder": 1,
                    "companyName": "CareerChat",
                    "position": "Backend Developer",
                    "content": "Python and Spring experience required.",
                },
            ],
        }
    )


def build_metadata() -> AnalysisMetadata:
    return AnalysisMetadata(
        pipelineVersion="ai-diagnosis-v1",
        promptSetVersion="diagnosis-prompt-set-v1",
        defaultModel="llama-3.3-70b-versatile",
        retrievalTopK=3,
    )


def test_task_payload_from_request_preserves_worker_fields() -> None:
    request = build_analysis_job_request()
    metadata = build_metadata()

    payload = AnalysisTaskPayload.from_request(
        request=request,
        task_id="task-1",
        metadata=metadata,
    )

    assert payload.diagnosisId == request.diagnosisId
    assert payload.taskId == "task-1"
    assert payload.callback == request.callback
    assert payload.profileSnapshot == request.profileSnapshot
    assert payload.jobs == request.jobs
    assert payload.metadata == metadata


def test_task_payload_converts_to_pipeline_context_without_callback() -> None:
    payload = AnalysisTaskPayload.from_request(
        request=build_analysis_job_request(),
        task_id="task-1",
        metadata=build_metadata(),
    )

    context = payload.to_pipeline_context()

    assert isinstance(context, AnalysisPipelineContext)
    assert context.diagnosisId == payload.diagnosisId
    assert context.taskId == payload.taskId
    assert context.profileSnapshot == payload.profileSnapshot
    assert context.jobs == payload.jobs
    assert context.metadata == payload.metadata
    assert not hasattr(context, "callback")


def test_task_payload_rejects_blank_task_id() -> None:
    with pytest.raises(ValidationError):
        AnalysisTaskPayload.from_request(
            request=build_analysis_job_request(),
            task_id="",
            metadata=build_metadata(),
        )


def test_task_payload_can_be_dumped_as_json_safe_dict() -> None:
    payload = AnalysisTaskPayload.from_request(
        request=build_analysis_job_request(),
        task_id="task-1",
        metadata=build_metadata(),
    )

    dumped = payload.model_dump(mode="json")

    assert dumped["taskId"] == "task-1"
    assert dumped["callback"]["completeUrl"].startswith("http://localhost:8080")
