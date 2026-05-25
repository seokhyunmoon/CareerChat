from __future__ import annotations

from app.pipeline.job_structuring import DeterministicJobRequirementExtractor
from app.schemas.analysis_job import AnalysisJobPosting


def test_deterministic_job_requirement_extractor_splits_lines_and_classifies() -> None:
    job = AnalysisJobPosting(
        jdId=10,
        displayOrder=1,
        companyName="CareerChat",
        position="Backend Developer",
        content="\n".join(
            [
                "- Spring Boot REST API 개발 경험",
                "- Redis 기반 비동기 처리 경험 우대",
            ]
        ),
    )

    requirements = DeterministicJobRequirementExtractor().extract_requirements(job)

    assert [requirement.requirementId for requirement in requirements] == [
        "jd-10-req-1",
        "jd-10-req-2",
    ]
    assert requirements[0].category == "skill"
    assert requirements[0].priority == "required"
    assert "spring boot" in requirements[0].keywords
    assert requirements[1].category == "preference"
    assert requirements[1].priority == "preferred"


def test_deterministic_job_requirement_extractor_falls_back_to_single_requirement() -> None:
    job = AnalysisJobPosting(
        jdId=10,
        displayOrder=1,
        companyName="CareerChat",
        position=None,
        content="백엔드 서비스 운영과 API 설계를 담당합니다",
    )

    requirements = DeterministicJobRequirementExtractor().extract_requirements(job)

    assert len(requirements) == 1
    assert requirements[0].description == "백엔드 서비스 운영과 API 설계를 담당합니다"
    assert requirements[0].category == "skill"
