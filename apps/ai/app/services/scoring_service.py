from __future__ import annotations

from app.schemas.match import RequirementMatch


def compute_fit_score(matches: list[RequirementMatch]) -> dict[str, float]:
    raw_score = sum(score_match(match.importance, match.match_level) for match in matches)
    max_score = sum(max_score_for_match(match.importance) for match in matches)
    fit_score = round((raw_score / max_score) * 100, 2) if max_score > 0 else 0.0

    return {
        "raw_score": raw_score,
        "max_score": max_score,
        "fit_score": fit_score,
    }


def score_match(importance: str, match_level: str) -> float:
    score_table = {
        ("required", "strong"): 1.0,
        ("required", "partial"): 0.6,
        ("required", "missing"): 0.0,
        ("preferred", "strong"): 0.5,
        ("preferred", "partial"): 0.25,
        ("preferred", "missing"): 0.0,
    }

    return score_table[(importance, match_level)]


def max_score_for_match(importance: str) -> float:
    return 1.0 if importance == "required" else 0.5
