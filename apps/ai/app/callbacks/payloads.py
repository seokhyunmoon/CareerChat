from __future__ import annotations

import json
from datetime import UTC, datetime

from app.core.error_codes import AnalysisErrorCode, is_retryable_error
from app.llm.errors import InvalidLLMResponseError, LLMProviderError, LLMTimeoutError
from app.pipeline.context import AnalysisPipelineResult
from app.schemas.analysis_result import JobAnalysisResult
from app.schemas.callback import (
    CompleteCallbackJobResult,
    CompleteCallbackPayload,
    FailCallbackPayload,
)
from app.workers.payloads import AnalysisTaskPayload


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def build_complete_callback_payload(
    *,
    result: AnalysisPipelineResult,
) -> CompleteCallbackPayload:
    report_package = result.reportPackage

    return CompleteCallbackPayload(
        taskId=result.taskId,
        reportSummary=report_package.reportSummary,
        reportContent=report_package.reportContent,
        completedAt=utc_now(),
        modelName=result.metadata.defaultModel,
        promptVersion=result.metadata.promptSetVersion,
        analysisMetadata=result.metadata.model_dump_json(),
        jobs=[
            _build_complete_callback_job_result(job)
            for job in report_package.jobs
        ],
    )


def _build_complete_callback_job_result(
    job: JobAnalysisResult,
) -> CompleteCallbackJobResult:
    return CompleteCallbackJobResult(
        jdId=job.jdId,
        rankOrder=job.rankOrder,
        fitScore=job.fitScore,
        strengthsSummary=job.strengthsSummary,
        gapsSummary=job.gapsSummary,
        highlightPoints=_dump_json_or_none(job.highlightPoints),
        matchDetails=json.dumps(
            [
                requirement_match.model_dump(mode="json")
                for requirement_match in job.requirementMatches
            ],
            ensure_ascii=False,
        ),
    )


def _dump_json_or_none(value: list[str]) -> str | None:
    if not value:
        return None
    return json.dumps(value, ensure_ascii=False)


def build_fail_callback_payload(
    *,
    task_payload: AnalysisTaskPayload,
    exc: Exception,
    failed_step: str | None = None,
    error_code: AnalysisErrorCode = AnalysisErrorCode.UNEXPECTED_ERROR,
) -> FailCallbackPayload:
    resolved_error_code = _resolve_error_code(exc=exc, fallback=error_code)
    error_message = str(exc).strip() or exc.__class__.__name__
    error_details = {
        "exceptionType": exc.__class__.__name__,
        "retryable": is_retryable_error(resolved_error_code),
    }

    return FailCallbackPayload(
        taskId=task_payload.taskId,
        errorCode=resolved_error_code.value,
        errorMessage=error_message,
        failedStep=failed_step,
        failedAt=utc_now(),
        errorDetails=json.dumps(error_details, ensure_ascii=False),
    )


def _resolve_error_code(
    *,
    exc: Exception,
    fallback: AnalysisErrorCode,
) -> AnalysisErrorCode:
    if fallback != AnalysisErrorCode.UNEXPECTED_ERROR:
        return fallback
    if isinstance(exc, LLMTimeoutError):
        return AnalysisErrorCode.LLM_TIMEOUT
    if isinstance(exc, LLMProviderError):
        return AnalysisErrorCode.LLM_PROVIDER_ERROR
    if isinstance(exc, InvalidLLMResponseError):
        return AnalysisErrorCode.INVALID_AI_RESPONSE
    return fallback
