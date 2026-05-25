from __future__ import annotations

from app.pipeline.scoring import RequirementScoringService
from app.schemas.analysis_result import JobRequirement, RequirementMatch


def build_match(
    *,
    requirement_id: str,
    status: str,
    priority: str,
) -> RequirementMatch:
    return RequirementMatch(
        requirement=JobRequirement(
            requirementId=requirement_id,
            priority=priority,
            description=requirement_id,
        ),
        status=status,
        confidenceScore=0.8,
    )


def test_requirement_scoring_service_calculates_weighted_fit_score() -> None:
    score = RequirementScoringService().calculate_fit_score(
        [
            build_match(
                requirement_id="required-match",
                status="matched",
                priority="required",
            ),
            build_match(
                requirement_id="preferred-partial",
                status="partial",
                priority="preferred",
            ),
            build_match(
                requirement_id="optional-missing",
                status="missing",
                priority="optional",
            ),
        ]
    )

    assert score == 64.3


def test_requirement_scoring_service_returns_zero_for_empty_matches() -> None:
    assert RequirementScoringService().calculate_fit_score([]) == 0.0
