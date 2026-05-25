from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from app.llm.errors import InvalidLLMResponseError
from app.llm.provider import LLMProvider, PromptExecutionResult
from app.llm.structured import RequirementMatchDecision, parse_structured_output
from app.prompts.templates import build_requirement_matching_prompt
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    JobRequirement,
    MatchedProfileEvidence,
    RequirementMatch,
)


class DeterministicRequirementMatcher:
    def __init__(
        self,
        *,
        matched_threshold: float = 0.65,
        partial_threshold: float = 0.25,
    ) -> None:
        if not 0 <= partial_threshold <= matched_threshold <= 1:
            raise ValueError("thresholds must satisfy 0 <= partial <= matched <= 1")

        self._matched_threshold = matched_threshold
        self._partial_threshold = partial_threshold

    def match_requirement(
        self,
        *,
        requirement: JobRequirement,
        evidence: Sequence[MatchedProfileEvidence],
    ) -> RequirementMatch:
        best_score = max((item.relevanceScore for item in evidence), default=0.0)

        if best_score >= self._matched_threshold:
            return RequirementMatch(
                requirement=requirement,
                status="matched",
                confidenceScore=round(best_score, 4),
                evidence=list(evidence),
                rationale="요구사항과 직접적으로 연결되는 프로필 근거를 찾았습니다.",
            )

        if best_score >= self._partial_threshold:
            return RequirementMatch(
                requirement=requirement,
                status="partial",
                confidenceScore=round(best_score, 4),
                evidence=list(evidence),
                rationale="일부 관련 근거는 있으나 요구사항을 완전히 충족한다고 보기 어렵습니다.",
                gap="요구사항을 명확히 입증할 추가 경험이나 성과 설명이 필요합니다.",
            )

        return RequirementMatch(
            requirement=requirement,
            status="missing",
            confidenceScore=0,
            evidence=[],
            rationale="요구사항과 연결되는 충분한 프로필 근거를 찾지 못했습니다.",
            gap="이 요구사항을 뒷받침할 프로젝트, 경력, 성과 내용을 보완해야 합니다.",
        )


@dataclass(frozen=True)
class RequirementMatchingResult:
    match: RequirementMatch
    execution: PromptExecutionResult


class LLMRequirementMatcher:
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

    def match_requirement(
        self,
        *,
        job: AnalysisJobPosting,
        requirement: JobRequirement,
        evidence: Sequence[MatchedProfileEvidence],
    ) -> RequirementMatchingResult:
        request = build_requirement_matching_prompt(
            job=job,
            requirement=requirement,
            evidence=evidence,
            model_name=self._model_name,
            temperature=self._temperature,
        )
        execution = self._llm_provider.execute_prompt(request)
        decision = parse_structured_output(
            content=execution.content,
            schema=RequirementMatchDecision,
        )

        selected_evidence = _select_evidence_by_index(
            evidence=evidence,
            indexes=decision.evidenceIndexes,
        )
        if decision.status == "missing":
            selected_evidence = []

        return RequirementMatchingResult(
            match=RequirementMatch(
                requirement=requirement,
                status=decision.status,
                confidenceScore=round(decision.confidenceScore, 4),
                evidence=selected_evidence,
                rationale=decision.rationale,
                gap=decision.gap,
            ),
            execution=execution,
        )


def _select_evidence_by_index(
    *,
    evidence: Sequence[MatchedProfileEvidence],
    indexes: Sequence[int],
) -> list[MatchedProfileEvidence]:
    selected_evidence = []
    for index in indexes:
        if index >= len(evidence):
            raise InvalidLLMResponseError(
                f"LLM returned evidence index outside range: {index}"
            )
        selected_evidence.append(evidence[index])

    return selected_evidence
