from __future__ import annotations

import json

import pytest

from app.core.pipeline_steps import PipelineStep
from app.llm.errors import InvalidLLMResponseError
from app.llm.provider import PromptExecutionRequest, PromptExecutionResult
from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.reporting import AnalysisReportGenerator
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


class FakeLLMProvider:
    provider_name = "fake"

    def __init__(self, responses: dict[str, list[dict]]) -> None:
        self.responses = {
            key: [json.dumps(item, ensure_ascii=False) for item in value]
            for key, value in responses.items()
        }
        self.requests: list[PromptExecutionRequest] = []

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult:
        self.requests.append(request)
        content = self.responses[request.promptKey].pop(0)
        return PromptExecutionResult(
            providerName=self.provider_name,
            modelName=request.modelName,
            promptKey=request.promptKey,
            promptVersion=request.promptVersion,
            content=content,
            durationMs=10,
            retryCount=0,
        )


class FailingLLMProvider:
    provider_name = "failing"

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult:
        raise InvalidLLMResponseError("bad LLM response")


def build_context() -> AnalysisPipelineContext:
    return AnalysisPipelineContext(
        diagnosisId=1,
        taskId="task-1",
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
            defaultModel="fake-model",
        ),
        profileSnapshot=ProfileSnapshot.model_validate(
            {
                "snapshotVersion": 1,
                "profile": {
                    "profileId": 10,
                    "experienceLevel": "junior",
                },
                "education": [],
                "workExperiences": [],
                "projects": [
                    {
                        "projectId": 3,
                        "projectName": "CareerChat",
                        "description": "Spring Boot REST API를 구현했습니다.",
                    }
                ],
                "achievements": [],
            }
        ),
        jobs=[
            AnalysisJobPosting(
                jdId=10,
                displayOrder=1,
                companyName="Backend Corp",
                position="Backend Developer",
                content="Spring Boot REST API 개발 경험",
            )
        ],
    )


def test_analysis_report_generator_uses_llm_provider_outputs() -> None:
    provider = FakeLLMProvider(
        {
            "job_structuring": [
                {
                    "requirements": [
                        {
                            "requirementId": "jd-10-req-1",
                            "category": "skill",
                            "priority": "required",
                            "description": "Spring Boot REST API 개발 경험",
                            "keywords": ["spring boot", "rest api"],
                            "sourceText": "Spring Boot REST API 개발 경험",
                        }
                    ]
                }
            ],
            "requirement_matching": [
                {
                    "status": "matched",
                    "confidenceScore": 0.92,
                    "evidenceIndexes": [0],
                    "rationale": "프로필 근거가 요구사항과 직접 연결됩니다.",
                    "gap": None,
                }
            ],
            "report_generation": [
                {
                    "reportSummary": "LLM summary",
                    "reportContent": "# LLM report",
                    "jobs": [
                        {
                            "jdId": 10,
                            "strengthsSummary": "LLM strengths",
                            "gapsSummary": "LLM gaps",
                            "highlightPoints": ["spring boot"],
                        }
                    ],
                }
            ],
        }
    )

    report = AnalysisReportGenerator(
        llm_provider=provider,
        llm_model_name="fake-model",
        llm_fallback_enabled=False,
    ).generate_report(build_context())

    assert [request.promptKey for request in provider.requests] == [
        "job_structuring",
        "requirement_matching",
        "report_generation",
    ]
    assert report.reportSummary == "LLM summary"
    assert report.reportContent == "# LLM report"
    assert report.jobs[0].strengthsSummary == "LLM strengths"
    assert report.jobs[0].requirementMatches[0].status == "matched"
    assert report.jobs[0].requirementMatches[0].evidence

    metadata = report.model_dump(mode="json")
    assert metadata["jobs"][0]["highlightPoints"] == ["spring boot"]


def test_analysis_report_generator_records_llm_step_metadata() -> None:
    context = build_context()
    provider = FakeLLMProvider(
        {
            "job_structuring": [
                {
                    "requirements": [
                        {
                            "requirementId": "jd-10-req-1",
                            "category": "skill",
                            "priority": "required",
                            "description": "Spring Boot REST API 개발 경험",
                            "keywords": ["spring boot"],
                            "sourceText": "Spring Boot REST API 개발 경험",
                        }
                    ]
                }
            ],
            "requirement_matching": [
                {
                    "status": "matched",
                    "confidenceScore": 0.9,
                    "evidenceIndexes": [0],
                    "rationale": "직접 연결됩니다.",
                    "gap": None,
                }
            ],
            "report_generation": [
                {
                    "reportSummary": "summary",
                    "reportContent": "content",
                    "jobs": [],
                }
            ],
        }
    )

    AnalysisReportGenerator(
        llm_provider=provider,
        llm_model_name="fake-model",
        llm_fallback_enabled=False,
    ).generate_report(context)

    step = context.metadata.steps[PipelineStep.JOB_STRUCTURING.value]
    assert step.providerName == "fake"
    assert step.modelName == "fake-model"
    assert step.promptVersion == "job-structuring-v1"
    assert step.fallbackUsed is False


def test_analysis_report_generator_falls_back_to_deterministic_provider() -> None:
    context = build_context()

    report = AnalysisReportGenerator(
        llm_provider=FailingLLMProvider(),
        llm_model_name="fake-model",
        llm_fallback_enabled=True,
    ).generate_report(context)

    assert report.reportSummary.startswith("Backend Corp")
    assert report.jobs[0].requirementMatches[0].status == "matched"
    assert (
        context.metadata.steps[PipelineStep.JOB_STRUCTURING.value].fallbackUsed
        is True
    )


def test_analysis_report_generator_can_disable_llm_fallback() -> None:
    with pytest.raises(InvalidLLMResponseError):
        AnalysisReportGenerator(
            llm_provider=FailingLLMProvider(),
            llm_model_name="fake-model",
            llm_fallback_enabled=False,
        ).generate_report(build_context())
