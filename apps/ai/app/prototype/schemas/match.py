from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class RequirementMatch(BaseModel):
    original_text: str
    normalized_text: str
    importance: Literal["required", "preferred"]
    match_level: Literal["strong", "partial", "missing"]
    reason: str = Field(description="왜 이렇게 판단했는지 한두 문장으로 설명")
    evidence: List[str] = Field(description="판단에 사용한 근거 문장 또는 요약")
