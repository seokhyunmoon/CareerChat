from __future__ import annotations

from typing import Any

from app.schemas.job import StructuredJobPosting
from app.schemas.match import RequirementMatch


def build_report_input(
    structured_job: StructuredJobPosting,
    matches: list[RequirementMatch],
    score_result: dict[str, float],
) -> dict[str, Any]:
    return {
        "company_name": structured_job.company_name,
        "position": structured_job.position,
        "job_context": structured_job.job_context,
        "fit_score": round(score_result["fit_score"], 1),
        "strong_matches": [
            {
                "normalized_text": match.normalized_text,
                "reason": match.reason,
                "evidence": match.evidence,
            }
            for match in matches
            if match.match_level == "strong"
        ],
        "partial_matches": [
            {
                "normalized_text": match.normalized_text,
                "reason": match.reason,
                "evidence": match.evidence,
            }
            for match in matches
            if match.match_level == "partial"
        ],
        "missing_matches": [
            {
                "normalized_text": match.normalized_text,
                "reason": match.reason,
                "evidence": match.evidence,
            }
            for match in matches
            if match.match_level == "missing"
        ],
    }


def generate_report(report_input: dict[str, Any], llm: Any) -> str:
    prompt = f"""
너는 개발자 채용공고 적합도 리포트를 작성하는 커리어 코치다.

아래 데이터를 기반으로 지원자와 채용공고의 적합도 리포트를 작성하라.

중요 규칙:
- 한국어로 작성
- evidence 기반으로만 설명
- strong_matches만 '확실한 강점'에 사용
- partial_matches와 missing_matches는 '보완이 필요한 부분'에 사용
- '관심', '가능성', '방향성'은 확실한 강점으로 과장하지 말 것
- fit_score는 휴리스틱 점수이므로 '약 XX점 수준'처럼 해석할 것
- 없는 경험을 있다고 쓰지 말 것
- 조언은 현재 가진 경험을 어떻게 강조하고 무엇을 보완할지 중심으로 작성

출력 형식:
1. 한 줄 총평
2. 적합도 요약
3. 확실한 강점
4. 보완이 필요한 부분
5. 지원서에서 강조할 경험
6. 지원 전략 조언

data:
{report_input}
    """.strip()

    return llm.invoke(prompt).content
