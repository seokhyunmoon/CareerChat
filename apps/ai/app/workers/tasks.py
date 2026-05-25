from __future__ import annotations

from typing import Any, Protocol

from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.orchestrator import AnalysisPipeline
from app.workers.celery_app import celery_app
from app.workers.payloads import AnalysisTaskPayload


class AnalysisPipelineRunner(Protocol):
    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult: ...


def run_analysis_payload(
    payload: AnalysisTaskPayload,
    pipeline: AnalysisPipelineRunner | None = None,
) -> AnalysisPipelineResult:
    analysis_pipeline = pipeline or AnalysisPipeline()
    return analysis_pipeline.run(payload.to_pipeline_context())


@celery_app.task(name="analysis.run")
def run_analysis_task(payload: dict[str, Any]) -> dict[str, Any]:
    task_payload = AnalysisTaskPayload.model_validate(payload)
    result = run_analysis_payload(task_payload)
    return result.model_dump(mode="json")


def enqueue_analysis_task(payload: AnalysisTaskPayload) -> Any:
    return run_analysis_task.delay(payload.model_dump(mode="json"))
