from __future__ import annotations

import pytest

from app.llm.errors import InvalidLLMResponseError
from app.llm.structured import (
    RequirementMatchDecision,
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
