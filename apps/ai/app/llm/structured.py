from __future__ import annotations

import json
from typing import TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from app.llm.errors import InvalidLLMResponseError
from app.schemas.analysis_result import (
    JobRequirement,
    RequirementMatchStatus,
)

StructuredOutputT = TypeVar("StructuredOutputT", bound=BaseModel)


class JobRequirementsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirements: list[JobRequirement] = Field(min_length=1, max_length=12)


class RequirementMatchDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: RequirementMatchStatus
    confidenceScore: float = Field(ge=0, le=1)
    evidenceIndexes: list[int] = Field(default_factory=list)
    rationale: str | None = None
    gap: str | None = None

    @field_validator("evidenceIndexes")
    @classmethod
    def validate_evidence_indexes(cls, indexes: list[int]) -> list[int]:
        if any(index < 0 for index in indexes):
            raise ValueError("evidenceIndexes must not contain negative values")
        if len(indexes) != len(set(indexes)):
            raise ValueError("evidenceIndexes must not contain duplicates")
        return indexes

    @model_validator(mode="after")
    def validate_missing_match_has_no_evidence_indexes(
        self,
    ) -> RequirementMatchDecision:
        if self.status == "missing" and self.evidenceIndexes:
            raise ValueError(
                "missing requirement matches must not contain evidenceIndexes"
            )
        return self


class ReportJobSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jdId: int = Field(ge=1)
    strengthsSummary: str | None = None
    gapsSummary: str | None = None
    highlightPoints: list[str] = Field(default_factory=list)


class ReportGenerationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reportSummary: str = Field(min_length=1)
    reportContent: str = Field(min_length=1)
    jobs: list[ReportJobSummary] = Field(default_factory=list)


RESPONSE_SCHEMAS: dict[str, type[BaseModel]] = {
    "JobRequirementsOutput": JobRequirementsOutput,
    "RequirementMatchDecision": RequirementMatchDecision,
    "ReportGenerationOutput": ReportGenerationOutput,
}


def parse_structured_output(
    *,
    content: str,
    schema: type[StructuredOutputT],
) -> StructuredOutputT:
    try:
        payload = json.loads(_extract_json_object(content))
    except json.JSONDecodeError as exc:
        raise InvalidLLMResponseError("LLM response is not valid JSON") from exc

    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise InvalidLLMResponseError(
            f"LLM response does not match {schema.__name__}"
        ) from exc


def resolve_response_schema(name: str) -> type[BaseModel]:
    try:
        return RESPONSE_SCHEMAS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown LLM response schema: {name}") from exc


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = _strip_markdown_fence(stripped)

    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return stripped
    return stripped[start : end + 1]


def _strip_markdown_fence(content: str) -> str:
    lines = content.splitlines()
    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return content
