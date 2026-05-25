from __future__ import annotations

import re
from dataclasses import dataclass

from app.llm.provider import LLMProvider, PromptExecutionResult
from app.llm.structured import JobRequirementsOutput, parse_structured_output
from app.pipeline.deterministic_text import KNOWN_MATCH_TERMS, extract_match_terms
from app.prompts.templates import build_job_structuring_prompt
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import JobRequirement

MAX_REQUIREMENTS_PER_JOB = 12

PREFERRED_MARKERS = ("우대", "preferred", "plus", "nice to have")
OPTIONAL_MARKERS = ("선택", "optional")
QUALIFICATION_MARKERS = ("자격", "필수", "required", "qualification")
RESPONSIBILITY_MARKERS = ("담당", "업무", "responsibility", "build", "implement", "구현", "설계")
EXPERIENCE_MARKERS = ("경험", "experience", "운영", "프로젝트")


class DeterministicJobRequirementExtractor:
    def extract_requirements(self, job: AnalysisJobPosting) -> list[JobRequirement]:
        candidates = _split_requirement_candidates(job.content)
        if not candidates:
            candidates = [job.content]

        requirements = []
        for index, candidate in enumerate(candidates[:MAX_REQUIREMENTS_PER_JOB]):
            requirements.append(
                JobRequirement(
                    requirementId=f"jd-{job.jdId}-req-{index + 1}",
                    category=_classify_category(candidate),
                    priority=_classify_priority(candidate),
                    description=candidate,
                    keywords=_extract_requirement_keywords(candidate),
                    sourceText=candidate,
                )
            )

        return requirements


@dataclass(frozen=True)
class JobRequirementExtractionResult:
    requirements: list[JobRequirement]
    execution: PromptExecutionResult


class LLMJobRequirementExtractor:
    def __init__(
        self,
        *,
        llm_provider: LLMProvider,
        model_name: str,
        temperature: float | None = None,
    ) -> None:
        self._llm_provider = llm_provider
        self._model_name = model_name
        self._temperature = temperature

    def extract_requirements(
        self,
        job: AnalysisJobPosting,
    ) -> JobRequirementExtractionResult:
        request = build_job_structuring_prompt(
            job=job,
            model_name=self._model_name,
            temperature=self._temperature,
        )
        execution = self._llm_provider.execute_prompt(request)
        output = parse_structured_output(
            content=execution.content,
            schema=JobRequirementsOutput,
        )

        return JobRequirementExtractionResult(
            requirements=output.requirements,
            execution=execution,
        )


def _split_requirement_candidates(content: str) -> list[str]:
    lines = []
    for raw_line in content.splitlines():
        line = _strip_bullet(raw_line)
        if line:
            lines.append(line)

    if len(lines) > 1:
        return lines

    sentence_parts = re.split(r"(?<=[.!?。])\s+", content)
    return [_strip_bullet(part) for part in sentence_parts if _strip_bullet(part)]


def _strip_bullet(value: str) -> str:
    return value.strip().lstrip("-*•·▪").strip()


def _classify_priority(text: str) -> str:
    normalized = text.lower()
    if any(marker in normalized for marker in PREFERRED_MARKERS):
        return "preferred"
    if any(marker in normalized for marker in OPTIONAL_MARKERS):
        return "optional"
    return "required"


def _classify_category(text: str) -> str:
    normalized = text.lower()
    if any(marker in normalized for marker in PREFERRED_MARKERS):
        return "preference"
    if any(term in normalized for term in KNOWN_MATCH_TERMS):
        return "skill"
    if any(marker in normalized for marker in RESPONSIBILITY_MARKERS):
        return "responsibility"
    if any(marker in normalized for marker in EXPERIENCE_MARKERS):
        return "experience"
    if any(marker in normalized for marker in QUALIFICATION_MARKERS):
        return "qualification"
    return "other"


def _extract_requirement_keywords(text: str) -> list[str]:
    return extract_match_terms(text)[:8]
