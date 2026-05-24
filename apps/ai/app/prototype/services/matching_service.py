from __future__ import annotations

from typing import Any

from app.prototype.schemas.job import StructuredRequirement
from app.prototype.schemas.match import RequirementMatch


def match_requirement(
    requirement: StructuredRequirement,
    retriever: Any,
    llm: Any,
    top_k: int = 3,
    requirement_matcher: Any | None = None,
) -> RequirementMatch:
    requirement_matcher = requirement_matcher or llm.with_structured_output(RequirementMatch)
    query = requirement.normalized_text
    retrieved_docs = retriever.invoke(query)

    evidence_text = "\n\n".join(
        [
            f"[{index + 1}] title={doc.metadata.get('title')}, type={doc.metadata.get('type')}\n{doc.page_content}"
            for index, doc in enumerate(retrieved_docs[:top_k])
        ]
    )

    prompt = f"""
너는 채용공고 requirement와 지원자 프로필 evidence를 비교하는 평가자다.

이번 평가는 normalized_text 기준으로 수행한다.
단, normalized_text가 복합 요구사항이면 그 복합 범위를 그대로 평가해야 한다.

예:
- "LLM, RAG, Agent 적용 경험"은 하나의 묶음 requirement로 본다
- 이 경우 일부 요소만 근거가 있으면 partial로 판단한다
- strong은 requirement 전체 범위를 충분히 뒷받침하는 근거가 있을 때만 준다

판단 기준:
- strong: normalized requirement 전체 범위에 직접 대응되는 구현/설계/운영 경험이 evidence에 분명히 존재
- partial: 관련 경험은 있으나 normalized requirement 전체를 완전히 충족한다고 보기엔 일부만 대응
- missing: evidence에서 직접적인 관련 근거를 찾기 어렵다

규칙:
- original_text는 출력에 그대로 유지하되 판정 기준은 normalized_text에 둔다
- reason은 1~2문장으로 간결하게 작성
- evidence는 실제 근거가 된 문장이나 요약 1~3개로 작성
- normalized_text와 직접 관련 없는 내용은 evidence에 넣지 않는다
- evidence에 없는 내용은 추정하지 않는다
- 복합 requirement일 경우, 어떤 요소가 충분하고 어떤 요소가 부족한지 reason에 반영할 수 있다

requirement.original_text:
{requirement.original_text}

requirement.normalized_text:
{requirement.normalized_text}

requirement.importance:
{requirement.importance}

retrieved evidence:
{evidence_text}
    """.strip()

    result = requirement_matcher.invoke(prompt)

    result.original_text = requirement.original_text
    result.normalized_text = requirement.normalized_text
    result.importance = requirement.importance

    return result


def match_requirements(
    requirements: list[StructuredRequirement],
    retriever: Any,
    llm: Any,
    top_k: int = 3,
) -> list[RequirementMatch]:
    requirement_matcher = llm.with_structured_output(RequirementMatch)

    return [
        match_requirement(
            requirement=requirement,
            retriever=retriever,
            llm=llm,
            top_k=top_k,
            requirement_matcher=requirement_matcher,
        )
        for requirement in requirements
    ]
