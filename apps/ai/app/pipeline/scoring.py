from __future__ import annotations

from collections.abc import Sequence

from app.schemas.analysis_result import RequirementMatch

STATUS_SCORE = {
    "matched": 1.0,
    "partial": 0.5,
    "missing": 0.0,
}

PRIORITY_WEIGHT = {
    "required": 1.0,
    "preferred": 0.7,
    "optional": 0.4,
}


class RequirementScoringService:
    def calculate_fit_score(self, matches: Sequence[RequirementMatch]) -> float:
        if not matches:
            return 0.0

        total_weight = 0.0
        weighted_score = 0.0
        for match in matches:
            weight = PRIORITY_WEIGHT[match.requirement.priority]
            total_weight += weight
            weighted_score += STATUS_SCORE[match.status] * weight

        if total_weight == 0:
            return 0.0

        return round((weighted_score / total_weight) * 100, 1)
