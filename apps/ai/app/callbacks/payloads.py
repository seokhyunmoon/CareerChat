from __future__ import annotations

import json
from datetime import UTC, datetime

from app.core.error_codes import AnalysisErrorCode, is_retryable_error
from app.pipeline.context import AnalysisPipelineResult
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
    task_payload: AnalysisTaskPayload,
    result: AnalysisPipelineResult,
) -> CompleteCallbackPayload:
    return CompleteCallbackPayload(
        taskId=result.taskId,
        reportSummary="AI analysis pipeline completed.",
        reportContent="{}",
        completedAt=utc_now(),
        modelName=result.metadata.defaultModel,
        promptVersion=result.metadata.promptSetVersion,
        analysisMetadata=result.metadata.model_dump_json(),
        jobs=[
            CompleteCallbackJobResult(
                jdId=job.jdId,
                rankOrder=job.displayOrder,
                fitScore=0,
                strengthsSummary=None,
                gapsSummary=None,
                highlightPoints=None,
                matchDetails="{}",
            )
            for job in task_payload.jobs
        ],
    )


def build_fail_callback_payload(
    *,
    task_payload: AnalysisTaskPayload,
    exc: Exception,
    failed_step: str | None = None,
    error_code: AnalysisErrorCode = AnalysisErrorCode.UNEXPECTED_ERROR,
) -> FailCallbackPayload:
    error_message = str(exc).strip() or exc.__class__.__name__
    error_details = {
        "exceptionType": exc.__class__.__name__,
        "retryable": is_retryable_error(error_code),
    }

    return FailCallbackPayload(
        taskId=task_payload.taskId,
        errorCode=error_code.value,
        errorMessage=error_message,
        failedStep=failed_step,
        failedAt=utc_now(),
        errorDetails=json.dumps(error_details, ensure_ascii=False),
    )
