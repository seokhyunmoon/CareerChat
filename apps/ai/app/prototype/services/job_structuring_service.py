from __future__ import annotations

import re
from typing import Any

from app.prototype.schemas.job import StructuredJobPosting


def structure_job_posting(job_posting: dict[str, Any], llm: Any) -> StructuredJobPosting:
    job_structurer = llm.with_structured_output(StructuredJobPosting)

    prompt = f"""
아래 개발자 채용공고를 읽고 비교 분석에 적합한 형태로 구조화하라.

출력은 두 부분으로 나눈다.

1. job_context
- 팀/포지션의 성격, 해결하려는 문제, 기술 환경, 시스템 방향성을 담는다
- 직접적인 지원자 자격요건이 아니라도, 이 직무의 맥락을 설명하는 핵심 내용을 3~6개 정도로 정리한다

2. requirements
- 지원자에게 요구하는 자격, 경험, 역량만 추출한다
- 필수 요건은 importance="required"
- 우대 요건은 importance="preferred"
- original_text는 원문 의미를 유지한다
- normalized_text는 검색과 비교가 쉬운 짧은 표현으로 정리한다
- tags는 1~5개의 핵심 기술/역량 태그로 작성한다
- 특정 직무 예시에 과적합되지 않도록 범용 개발 공고 기준으로 해석한다
- 중복되는 요구사항은 합쳐도 된다

가장 중요한 규칙:
- original_text와 normalized_text의 평가 단위는 반드시 일치해야 한다
- original_text가 여러 기술/역량을 묶은 복합 요구사항이면 normalized_text도 같은 범위를 유지한다
- original_text가 단일 기술/역량이면 normalized_text도 단일 기술/역량으로 정리한다
- 복합 요구사항을 부분적으로만 축약하지 않는다
- 예:
  - original_text가 "LLM, RAG, Agent와 같은 기술을 실제 문제에 적용해본 경험"이면
    normalized_text도 "LLM, RAG, Agent 적용 경험"처럼 같은 범위를 유지한다
  - 이 경우 "LLM 적용 경험"처럼 일부만 남기는 표현은 금지한다
- 이번 구조화에서는 requirement를 원자적으로 분해하지 않는다
- 즉, 복합 요구사항은 복합 요구사항으로 유지한다

company_name: {job_posting['company_name']}
position: {job_posting['position']}

posting:
{job_posting['content']}
    """.strip()

    return job_structurer.invoke(prompt)


def normalize_tag(tag: str) -> str:
    tag = tag.strip().lower()
    tag = tag.replace("-", "_").replace(" ", "_")
    tag = re.sub(r"__+", "_", tag)

    mapping = {
        "llm": "llm",
        "rag": "rag",
        "agent": "agent",
        "문제_해결": "problem_solving",
        "팀_협업": "team_collaboration",
        "기술_추적": "tech_trend",
        "사용자_경험": "user_experience",
        "플랫폼": "platform",
        "시스템_확장": "scalability",
    }

    return mapping.get(tag, tag)


def normalize_requirement_tags(job: StructuredJobPosting) -> StructuredJobPosting:
    for requirement in job.requirements:
        requirement.tags = [normalize_tag(tag) for tag in requirement.tags]

    return job
