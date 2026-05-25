from __future__ import annotations

from typing import Any, Protocol

from app.callbacks.client import build_spring_callback_client
from app.callbacks.payloads import (
    build_complete_callback_payload,
    build_fail_callback_payload,
)
from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.orchestrator import AnalysisPipeline
from app.schemas.analysis_job import CallbackTarget
from app.schemas.callback import CompleteCallbackPayload, FailCallbackPayload
from app.workers.celery_app import celery_app
from app.workers.payloads import AnalysisTaskPayload


class AnalysisPipelineRunner(Protocol):
    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult: ...


class SpringCallbackSender(Protocol):
    def post_complete(
        self,
        *,
        callback: CallbackTarget,
        payload: CompleteCallbackPayload,
    ) -> Any: ...

    def post_fail(
        self,
        *,
        callback: CallbackTarget,
        payload: FailCallbackPayload,
    ) -> Any: ...


def run_analysis_payload(
    payload: AnalysisTaskPayload,
    pipeline: AnalysisPipelineRunner | None = None,
) -> AnalysisPipelineResult:
    analysis_pipeline = pipeline or AnalysisPipeline()
    return analysis_pipeline.run(payload.to_pipeline_context())


def execute_analysis_task(
    payload: AnalysisTaskPayload,
    *,
    pipeline: AnalysisPipelineRunner | None = None,
    callback_client: SpringCallbackSender | None = None,
) -> AnalysisPipelineResult:
    spring_callback_client = callback_client or build_spring_callback_client()

    try:
        result = run_analysis_payload(payload, pipeline=pipeline)
    except Exception as exc:
        fail_payload = build_fail_callback_payload(
            task_payload=payload,
            exc=exc,
        )
        spring_callback_client.post_fail(
            callback=payload.callback,
            payload=fail_payload,
        )
        raise

    complete_payload = build_complete_callback_payload(
        task_payload=payload,
        result=result,
    )
    spring_callback_client.post_complete(
        callback=payload.callback,
        payload=complete_payload,
    )
    return result


@celery_app.task(name="analysis.run")
def run_analysis_task(payload: dict[str, Any]) -> dict[str, Any]:
    task_payload = AnalysisTaskPayload.model_validate(payload)
    result = execute_analysis_task(task_payload)
    return result.model_dump(mode="json")


def enqueue_analysis_task(payload: AnalysisTaskPayload) -> Any:
    return run_analysis_task.delay(payload.model_dump(mode="json"))
