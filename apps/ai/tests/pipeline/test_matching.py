from __future__ import annotations

import pytest

from app.pipeline.matching import DeterministicRequirementMatcher
from app.schemas.analysis_result import (
    JobRequirement,
    MatchedProfileEvidence,
)


def build_requirement() -> JobRequirement:
    return JobRequirement(
        requirementId="req-1",
        category="skill",
        priority="required",
        description="Spring Boot REST API 개발 경험",
        keywords=["spring boot", "rest api"],
    )


def build_evidence(relevance_score: float) -> MatchedProfileEvidence:
    return MatchedProfileEvidence(
        evidence={
            "sourceType": "project",
            "sourceId": 3,
            "chunkIndex": 0,
            "title": "CareerChat",
            "text": "Spring Boot REST API 구현 경험",
        },
        relevanceScore=relevance_score,
    )


@pytest.mark.parametrize(
    ("relevance_score", "expected_status"),
    [
        (0.8, "matched"),
        (0.4, "partial"),
    ],
)
def test_deterministic_requirement_matcher_classifies_evidence_score(
    relevance_score: float,
    expected_status: str,
) -> None:
    match = DeterministicRequirementMatcher().match_requirement(
        requirement=build_requirement(),
        evidence=[build_evidence(relevance_score)],
    )

    assert match.status == expected_status
    assert match.evidence


def test_deterministic_requirement_matcher_returns_missing_without_evidence() -> None:
    match = DeterministicRequirementMatcher().match_requirement(
        requirement=build_requirement(),
        evidence=[],
    )

    assert match.status == "missing"
    assert match.confidenceScore == 0
    assert match.evidence == []
    assert match.gap is not None


def test_deterministic_requirement_matcher_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError, match="thresholds"):
        DeterministicRequirementMatcher(matched_threshold=0.2, partial_threshold=0.5)
