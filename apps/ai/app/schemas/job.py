from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class StructuredRequirement(BaseModel):
    original_text: str = Field(description="공고 원문에서 추출한 요구사항")
    normalized_text: str = Field(description="비교 가능한 짧은 요구사항 표현")
    importance: Literal["required", "preferred"] = Field(
        description="필수 요건이면 required, 우대 요건이면 preferred"
    )
    tags: List[str] = Field(
        description="핵심 기술/역량 태그 목록. 예: python, spring_boot, backend, llm, rag, collaboration"
    )


class StructuredJobPosting(BaseModel):
    company_name: str
    position: str
    job_context: List[str] = Field(
        description="팀/포지션 맥락을 설명하는 핵심 문장 목록. 예: AI 플랫폼 팀, RAG/Agent 실험 및 운영, 확장 가능한 구조 설계"
    )
    requirements: List[StructuredRequirement]
