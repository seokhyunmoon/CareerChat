from __future__ import annotations

import pytest

from app.llm.errors import InvalidLLMResponseError
from app.llm.structured import (
    RequirementMatchDecision,
    ResultChatResponseOutput,
    parse_structured_output,
    resolve_response_schema,
)


def test_parse_structured_output_accepts_json_fence() -> None:
    parsed = parse_structured_output(
        content="""```json
{"status": "matched", "confidenceScore": 0.9, "evidenceIndexes": [0]}
```""",
        schema=RequirementMatchDecision,
    )

    assert parsed.status == "matched"
    assert parsed.confidenceScore == 0.9
    assert parsed.evidenceIndexes == [0]


def test_parse_structured_output_rejects_invalid_schema() -> None:
    with pytest.raises(InvalidLLMResponseError, match="does not match"):
        parse_structured_output(
            content='{"status": "unknown", "confidenceScore": 2}',
            schema=RequirementMatchDecision,
        )


def test_resolve_response_schema_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unknown LLM response schema"):
        resolve_response_schema("UnknownOutput")


def test_parse_structured_output_accepts_result_chat_response() -> None:
    parsed = parse_structured_output(
        content="""
        {
          "content": "토스 공고를 먼저 지원하는 것이 좋습니다.",
          "referencedJobIds": [10],
          "reasonCodes": ["TOP_RANKED_JOB"],
          "usedFields": ["jobResults.rankOrder"]
        }
        """,
        schema=ResultChatResponseOutput,
    )

    assert parsed.content.startswith("토스")
    assert parsed.referencedJobIds == [10]
    assert parsed.reasonCodes == ["TOP_RANKED_JOB"]
