from __future__ import annotations

import pytest
from pydantic import ValidationError

import app.workers.tasks as tasks_module
from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.reporting import AnalysisReportGenerator
from app.schemas.callback import CompleteCallbackPayload, FailCallbackPayload
from app.schemas.metadata import AnalysisMetadata
from app.workers.celery_app import celery_app
from app.workers.payloads import AnalysisTaskPayload
from app.workers.tasks import execute_analysis_task, run_analysis_payload, run_analysis_task
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
            reportPackage=AnalysisReportGenerator().generate_report(context),
        )


class FailingPipeline:
    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult:
        raise RuntimeError("pipeline failed")


class FakeCallbackClient:
    def __init__(self) -> None:
        self.complete_payloads: list[CompleteCallbackPayload] = []
        self.fail_payloads: list[FailCallbackPayload] = []

    def post_complete(self, *, callback, payload: CompleteCallbackPayload) -> None:
        self.complete_payloads.append(payload)

    def post_fail(self, *, callback, payload: FailCallbackPayload) -> None:
        self.fail_payloads.append(payload)


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


def test_execute_analysis_task_posts_complete_callback_on_success() -> None:
    payload = AnalysisTaskPayload.model_validate(build_payload_dict())
    pipeline = FakePipeline()
    callback_client = FakeCallbackClient()

    result = execute_analysis_task(
        payload,
        pipeline=pipeline,
        callback_client=callback_client,
    )

    assert result.taskId == payload.taskId
    assert len(callback_client.complete_payloads) == 1
    assert callback_client.complete_payloads[0].taskId == payload.taskId
    assert callback_client.complete_payloads[0].jobs[0].jdId == payload.jobs[0].jdId
    assert callback_client.fail_payloads == []


def test_execute_analysis_task_posts_fail_callback_and_reraises_on_failure() -> None:
    payload = AnalysisTaskPayload.model_validate(build_payload_dict())
    callback_client = FakeCallbackClient()

    with pytest.raises(RuntimeError, match="pipeline failed"):
        execute_analysis_task(
            payload,
            pipeline=FailingPipeline(),
            callback_client=callback_client,
        )

    assert callback_client.complete_payloads == []
    assert len(callback_client.fail_payloads) == 1
    assert callback_client.fail_payloads[0].taskId == payload.taskId
    assert callback_client.fail_payloads[0].errorCode == "UNEXPECTED_ERROR"
    assert callback_client.fail_payloads[0].errorMessage == "pipeline failed"


def test_run_analysis_task_rejects_invalid_payload() -> None:
    payload = build_payload_dict()
    payload["taskId"] = ""

    with pytest.raises(ValidationError):
        run_analysis_task(payload)


def test_run_analysis_task_uses_default_pipeline_and_posts_complete_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    callback_client = FakeCallbackClient()
    monkeypatch.setattr(
        tasks_module,
        "build_spring_callback_client",
        lambda: callback_client,
    )

    result = run_analysis_task(build_payload_dict())

    assert result["taskId"] == "task-1"
    assert result["reportPackage"]["taskId"] == "task-1"
    assert len(callback_client.complete_payloads) == 1
    assert callback_client.complete_payloads[0].taskId == "task-1"
    assert callback_client.fail_payloads == []
