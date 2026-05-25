from __future__ import annotations

from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.reporting import AnalysisReportGenerator
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


def build_context() -> AnalysisPipelineContext:
    return AnalysisPipelineContext(
        diagnosisId=1,
        taskId="task-1",
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
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
                        "description": (
                            "Spring Boot REST API와 Redis 기반 비동기 작업을 구현했습니다."
                        ),
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
                content="\n".join(
                    [
                        "- Spring Boot REST API 개발 경험",
                        "- Redis 기반 비동기 처리 경험 우대",
                    ]
                ),
            ),
            AnalysisJobPosting(
                jdId=11,
                displayOrder=2,
                companyName="Infra Corp",
                position="Platform Engineer",
                content="\n".join(
                    [
                        "- Kubernetes 운영 경험",
                        "- Terraform 기반 인프라 자동화 경험",
                    ]
                ),
            ),
        ],
    )


def test_analysis_report_generator_builds_ranked_report_package() -> None:
    report = AnalysisReportGenerator().generate_report(build_context())

    assert report.diagnosisId == 1
    assert report.taskId == "task-1"
    assert report.jobs[0].jdId == 10
    assert report.jobs[0].rankOrder == 1
    assert report.jobs[0].fitScore > report.jobs[1].fitScore
    assert report.jobs[0].requirementMatches[0].status == "matched"
    assert report.reportSummary.startswith("가장 적합한 공고는 Backend Corp")
    assert "# AI 분석 리포트" in report.reportContent


def test_analysis_report_generator_rejects_invalid_retrieval_top_k() -> None:
    try:
        AnalysisReportGenerator(retrieval_top_k=0)
    except ValueError as exc:
        assert "retrieval_top_k" in str(exc)
    else:
        raise AssertionError("AnalysisReportGenerator should reject retrieval_top_k=0")
