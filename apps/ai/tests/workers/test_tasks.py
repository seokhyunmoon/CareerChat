from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.schemas.metadata import AnalysisMetadata
from app.workers.celery_app import celery_app
from app.workers.payloads import AnalysisTaskPayload
from app.workers.tasks import run_analysis_payload, run_analysis_task
from tests.workers.test_payloads import build_analysis_job_request


class FakePipeline:
    def __init__(self) -> None:
        self.contexts: list[AnalysisPipelineContext] = []

    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult:
        self.contexts.append(context)
        return AnalysisPipelineResult(
            diagnosisId=context.diagnosisId,
            taskId=context.taskId,
            metadata=context.metadata,
        )


def build_payload_dict() -> dict:
    payload = AnalysisTaskPayload.from_request(
        request=build_analysis_job_request(),
        task_id="task-1",
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
        ),
    )
    return payload.model_dump(mode="json")


def test_run_analysis_task_is_registered() -> None:
    assert "analysis.run" in celery_app.tasks


def test_run_analysis_payload_builds_context_and_returns_pipeline_result() -> None:
    payload = AnalysisTaskPayload.model_validate(build_payload_dict())
    pipeline = FakePipeline()

    result = run_analysis_payload(payload, pipeline=pipeline)

    assert result.diagnosisId == payload.diagnosisId
    assert result.taskId == payload.taskId
    assert result.metadata == payload.metadata
    assert len(pipeline.contexts) == 1
    context = pipeline.contexts[0]
    assert context.diagnosisId == payload.diagnosisId
    assert context.taskId == payload.taskId
    assert context.profileSnapshot == payload.profileSnapshot
    assert context.jobs == payload.jobs
    assert context.metadata == payload.metadata
    assert not hasattr(context, "callback")


def test_run_analysis_task_rejects_invalid_payload() -> None:
    payload = build_payload_dict()
    payload["taskId"] = ""

    with pytest.raises(ValidationError):
        run_analysis_task(payload)


def test_run_analysis_task_raises_until_default_pipeline_is_implemented() -> None:
    with pytest.raises(NotImplementedError):
        run_analysis_task(build_payload_dict())
