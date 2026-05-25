from __future__ import annotations

import json

from app.callbacks.payloads import (
    build_complete_callback_payload,
    build_fail_callback_payload,
)
from app.core.error_codes import AnalysisErrorCode
from app.pipeline.context import AnalysisPipelineResult
from app.pipeline.reporting import AnalysisReportGenerator
from app.schemas.metadata import AnalysisMetadata
from app.workers.payloads import AnalysisTaskPayload
from tests.workers.test_payloads import build_analysis_job_request


def build_task_payload() -> AnalysisTaskPayload:
    return AnalysisTaskPayload.from_request(
        request=build_analysis_job_request(),
        task_id="task-1",
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
            defaultModel="llama-3.3-70b-versatile",
        ),
    )


def build_pipeline_result(task_payload: AnalysisTaskPayload) -> AnalysisPipelineResult:
    context = task_payload.to_pipeline_context()
    report_package = AnalysisReportGenerator().generate_report(context)

    return AnalysisPipelineResult(
        diagnosisId=task_payload.diagnosisId,
        taskId=task_payload.taskId,
        metadata=task_payload.metadata,
        reportPackage=report_package,
    )


def test_build_complete_callback_payload_returns_spring_contract_payload() -> None:
    task_payload = build_task_payload()
    result = build_pipeline_result(task_payload)

    callback_payload = build_complete_callback_payload(
        result=result,
    )

    assert callback_payload.taskId == "task-1"
    assert callback_payload.reportSummary == result.reportPackage.reportSummary
    assert callback_payload.reportContent == result.reportPackage.reportContent
    assert callback_payload.completedAt.tzinfo is None
    assert callback_payload.modelName == "llama-3.3-70b-versatile"
    assert callback_payload.promptVersion == "diagnosis-prompt-set-v1"
    assert (
        json.loads(callback_payload.analysisMetadata or "{}")["pipelineVersion"]
        == "ai-diagnosis-v1"
    )
    assert len(callback_payload.jobs) == 1
    assert callback_payload.jobs[0].jdId == result.reportPackage.jobs[0].jdId
    assert callback_payload.jobs[0].rankOrder == result.reportPackage.jobs[0].rankOrder
    assert callback_payload.jobs[0].fitScore == result.reportPackage.jobs[0].fitScore
    assert (
        callback_payload.jobs[0].strengthsSummary
        == result.reportPackage.jobs[0].strengthsSummary
    )
    assert (
        callback_payload.jobs[0].gapsSummary
        == result.reportPackage.jobs[0].gapsSummary
    )

    match_details = json.loads(callback_payload.jobs[0].matchDetails or "[]")
    assert match_details[0]["requirement"]["requirementId"] == "jd-1-req-1"
    assert match_details[0]["status"] == "missing"


def test_build_complete_callback_payload_serializes_highlight_points() -> None:
    task_payload = build_task_payload()
    result = build_pipeline_result(task_payload)
    job_result = result.reportPackage.jobs[0].model_copy(
        update={"highlightPoints": ["python", "spring"]}
    )
    report_package = result.reportPackage.model_copy(update={"jobs": [job_result]})
    result = result.model_copy(update={"reportPackage": report_package})

    callback_payload = build_complete_callback_payload(
        result=result,
    )

    assert json.loads(callback_payload.jobs[0].highlightPoints or "[]") == [
        "python",
        "spring",
    ]


def test_build_fail_callback_payload_returns_retryable_error_details() -> None:
    task_payload = build_task_payload()

    callback_payload = build_fail_callback_payload(
        task_payload=task_payload,
        exc=TimeoutError("LLM request timed out"),
        failed_step="REPORT_GENERATION",
        error_code=AnalysisErrorCode.LLM_TIMEOUT,
    )

    assert callback_payload.taskId == "task-1"
    assert callback_payload.errorCode == "LLM_TIMEOUT"
    assert callback_payload.errorMessage == "LLM request timed out"
    assert callback_payload.failedStep == "REPORT_GENERATION"
    assert callback_payload.failedAt.tzinfo is None

    error_details = json.loads(callback_payload.errorDetails or "{}")
    assert error_details == {
        "exceptionType": "TimeoutError",
        "retryable": True,
    }


def test_build_fail_callback_payload_uses_exception_type_when_message_is_blank() -> None:
    task_payload = build_task_payload()

    callback_payload = build_fail_callback_payload(
        task_payload=task_payload,
        exc=RuntimeError(),
    )

    assert callback_payload.errorCode == "UNEXPECTED_ERROR"
    assert callback_payload.errorMessage == "RuntimeError"
