from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.analysis_result import (
    AnalysisReportPackage,
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
    RequirementMatch,
)


def build_requirement() -> JobRequirement:
    return JobRequirement(
        requirementId="req-1",
        category="skill",
        priority="required",
        description="Spring Boot REST API development experience",
        keywords=["Spring Boot", "REST API"],
        sourceText="Spring Boot REST API experience required",
    )


def build_evidence() -> MatchedProfileEvidence:
    return MatchedProfileEvidence(
        evidence={
            "sourceType": "project",
            "sourceId": 3,
            "chunkIndex": 0,
            "title": "CareerChat",
            "text": "Implemented REST APIs with Spring Boot.",
        },
        relevanceScore=0.91,
        rationale="The project mentions Spring Boot REST API implementation.",
    )


def test_analysis_report_package_serializes_nested_matching_result() -> None:
    report = AnalysisReportPackage(
        diagnosisId=1,
        taskId="task-1",
        reportSummary="CareerChat has strong backend fit.",
        reportContent="Detailed report content",
        jobs=[
            JobAnalysisResult(
                jdId=10,
                rankOrder=1,
                companyName="CareerChat",
                position="Backend Developer",
                fitScore=86.5,
                strengthsSummary="Spring Boot project experience is relevant.",
                gapsSummary="Production traffic experience is limited.",
                highlightPoints=["Spring Boot", "REST API"],
                requirementMatches=[
                    RequirementMatch(
                        requirement=build_requirement(),
                        status="matched",
                        confidenceScore=0.88,
                        evidence=[build_evidence()],
                        rationale="Relevant project evidence was found.",
                    )
                ],
            )
        ],
    )

    payload = report.model_dump()

    assert payload["diagnosisId"] == 1
    assert payload["jobs"][0]["fitScore"] == 86.5
    assert payload["jobs"][0]["requirementMatches"][0]["status"] == "matched"
    assert (
        payload["jobs"][0]["requirementMatches"][0]["evidence"][0]["evidence"][
            "sourceType"
        ]
        == "project"
    )


def test_missing_requirement_match_rejects_evidence() -> None:
    with pytest.raises(ValidationError, match="must not contain evidence"):
        RequirementMatch(
            requirement=build_requirement(),
            status="missing",
            confidenceScore=0.1,
            evidence=[build_evidence()],
        )


def test_analysis_report_package_rejects_duplicate_job_rank() -> None:
    job = JobAnalysisResult(
        jdId=10,
        rankOrder=1,
        companyName="CareerChat",
        fitScore=80,
    )

    with pytest.raises(ValidationError, match="duplicate rankOrder"):
        AnalysisReportPackage(
            diagnosisId=1,
            taskId="task-1",
            reportSummary="summary",
            reportContent="content",
            jobs=[
                job,
                job.model_copy(update={"jdId": 11}),
            ],
        )


def test_analysis_report_package_rejects_duplicate_job_id() -> None:
    job = JobAnalysisResult(
        jdId=10,
        rankOrder=1,
        companyName="CareerChat",
        fitScore=80,
    )

    with pytest.raises(ValidationError, match="duplicate jdId"):
        AnalysisReportPackage(
            diagnosisId=1,
            taskId="task-1",
            reportSummary="summary",
            reportContent="content",
            jobs=[
                job,
                job.model_copy(update={"rankOrder": 2}),
            ],
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("fitScore", -1),
        ("fitScore", 101),
    ],
)
def test_job_analysis_result_rejects_invalid_fit_score(
    field: str,
    value: float,
) -> None:
    with pytest.raises(ValidationError):
        JobAnalysisResult(
            jdId=10,
            rankOrder=1,
            companyName="CareerChat",
            **{field: value},
        )
