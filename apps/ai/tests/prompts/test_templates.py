from __future__ import annotations

import pytest

from app.prompts import (
    JOB_STRUCTURING_PROMPT,
    REPORT_GENERATION_PROMPT,
    REQUIREMENT_MATCHING_PROMPT,
    build_job_structuring_prompt,
    build_report_generation_prompt,
    build_requirement_matching_prompt,
    render_prompt_template,
)
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
    RequirementMatch,
)


def test_prompt_manifest_points_to_versioned_template_files() -> None:
    assert JOB_STRUCTURING_PROMPT.template_path == "job_structuring_v1.md"
    assert REQUIREMENT_MATCHING_PROMPT.template_path == "requirement_matching_v1.md"
    assert REPORT_GENERATION_PROMPT.template_path == "report_generation_v1.md"


def test_render_prompt_template_rejects_unknown_file() -> None:
    with pytest.raises(FileNotFoundError):
        render_prompt_template("unknown_v1.md")


def test_render_prompt_template_splits_system_and_user_sections() -> None:
    rendered = render_prompt_template(
        "job_structuring_v1.md",
        {"payload_json": '{"job": {"jdId": 10}}'},
    )

    assert "채용공고를 분석" in rendered.system_prompt
    assert "payload:" in rendered.user_prompt
    assert '"jdId": 10' in rendered.user_prompt


def test_job_structuring_prompt_includes_quality_rules() -> None:
    request = build_job_structuring_prompt(
        job=AnalysisJobPosting(
            jdId=10,
            displayOrder=1,
            companyName="CareerChat",
            position="AI Engineer",
            content="LLM, RAG, Agent와 같은 기술을 실제 문제에 적용해본 경험",
        ),
        model_name="fake-model",
    )

    assert request.promptVersion == "job-structuring-v1"
    assert "복합 요구사항은 복합 요구사항으로 유지" in request.systemPrompt
    assert "sourceText와 description의 평가 단위" in request.systemPrompt
    assert '"jdId": 10' in request.userPrompt


def test_requirement_matching_prompt_includes_evidence_rules() -> None:
    requirement = JobRequirement(
        requirementId="jd-10-req-1",
        category="skill",
        priority="required",
        description="LLM, RAG, Agent 적용 경험",
        keywords=["llm", "rag", "agent"],
        sourceText="LLM, RAG, Agent와 같은 기술을 실제 문제에 적용해본 경험",
    )
    evidence = [
        MatchedProfileEvidence(
            evidence={
                "sourceType": "project",
                "sourceId": 1,
                "chunkIndex": 0,
                "title": "RAG project",
                "text": "RAG 기반 검색을 구현했습니다.",
            },
            relevanceScore=0.8,
        )
    ]

    request = build_requirement_matching_prompt(
        job=AnalysisJobPosting(
            jdId=10,
            displayOrder=1,
            companyName="CareerChat",
            position="AI Engineer",
            content="content",
        ),
        requirement=requirement,
        evidence=evidence,
        model_name="fake-model",
    )

    assert request.promptVersion == "requirement-matching-v1"
    assert "일부 요소만 evidence에 있으면 matched가 아니라 partial" in request.systemPrompt
    assert "evidenceIndexes에는 입력 evidence 배열에 존재하는 index만" in request.systemPrompt
    assert '"index": 0' in request.userPrompt


def test_report_generation_prompt_includes_user_facing_report_shape() -> None:
    requirement = JobRequirement(
        requirementId="jd-10-req-1",
        category="skill",
        priority="required",
        description="Spring Boot REST API 개발 경험",
        keywords=["spring boot"],
    )
    match = RequirementMatch(
        requirement=requirement,
        status="matched",
        confidenceScore=0.9,
        evidence=[],
    )

    request = build_report_generation_prompt(
        job_results=[
            JobAnalysisResult(
                jdId=10,
                rankOrder=1,
                companyName="Backend Corp",
                position="Backend Developer",
                fitScore=90,
                requirementMatches=[match],
            )
        ],
        model_name="fake-model",
    )

    assert request.promptVersion == "report-generation-v1"
    assert "지원서에서 강조할 경험" in request.systemPrompt
    assert "matched 요구사항만 확실한 강점" in request.systemPrompt
    assert '"fitScore": 90.0' in request.userPrompt
