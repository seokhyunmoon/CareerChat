from __future__ import annotations

from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.orchestrator import AnalysisPipeline
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import AnalysisReportPackage
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


class FakeReportGenerator:
    def __init__(self, report_package: AnalysisReportPackage) -> None:
        self.report_package = report_package
        self.contexts: list[AnalysisPipelineContext] = []

    def generate_report(self, context: AnalysisPipelineContext) -> AnalysisReportPackage:
        self.contexts.append(context)
        return self.report_package


def build_context() -> AnalysisPipelineContext:
    return AnalysisPipelineContext(
        diagnosisId=1,
        taskId="task-1",
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
                        "description": "Spring Boot REST API 구현",
                    }
                ],
                "achievements": [],
            }
        ),
        jobs=[
            AnalysisJobPosting(
                jdId=10,
                displayOrder=1,
                companyName="CareerChat",
                position="Backend Developer",
                content="Spring Boot REST API 개발 경험",
            )
        ],
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
        ),
    )


def build_report_package() -> AnalysisReportPackage:
    return AnalysisReportPackage(
        diagnosisId=1,
        taskId="task-1",
        reportSummary="summary",
        reportContent="content",
        jobs=[
            {
                "jdId": 10,
                "rankOrder": 1,
                "companyName": "CareerChat",
                "position": "Backend Developer",
                "fitScore": 90,
            }
        ],
    )


def test_analysis_pipeline_returns_report_package_from_generator() -> None:
    context = build_context()
    report_package = build_report_package()
    report_generator = FakeReportGenerator(report_package)
    pipeline = AnalysisPipeline(report_generator=report_generator)

    result = pipeline.run(context)

    assert result.diagnosisId == context.diagnosisId
    assert result.taskId == context.taskId
    assert result.metadata == context.metadata
    assert result.reportPackage == report_package
    assert report_generator.contexts == [context]


def test_analysis_pipeline_default_generator_builds_report_package() -> None:
    context = build_context()

    result = AnalysisPipeline().run(context)

    assert result.reportPackage.diagnosisId == context.diagnosisId
    assert result.reportPackage.taskId == context.taskId
    assert result.reportPackage.jobs[0].jdId == context.jobs[0].jdId
    assert result.reportPackage.jobs[0].fitScore > 0
