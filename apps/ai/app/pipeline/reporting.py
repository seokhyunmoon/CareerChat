from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.core.pipeline_steps import PipelineStep
from app.llm.errors import LLMExecutionError
from app.llm.factory import build_groq_llm_provider
from app.llm.provider import LLMProvider, PromptExecutionResult
from app.llm.structured import ReportGenerationOutput, parse_structured_output
from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.evidence_retrieval import (
    ProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.pipeline.job_structuring import (
    DeterministicJobRequirementExtractor,
    LLMJobRequirementExtractor,
)
from app.pipeline.matching import (
    DeterministicRequirementMatcher,
    LLMRequirementMatcher,
)
from app.pipeline.scoring import RequirementScoringService
from app.prompts.templates import build_report_generation_prompt
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    AnalysisReportPackage,
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
    RequirementMatch,
)
from app.schemas.metadata import AnalysisMetadata, AnalysisStepMetadata


@dataclass(frozen=True)
class _JobAnalysisDraft:
    job: AnalysisJobPosting
    fit_score: float
    requirement_matches: list[RequirementMatch]


@dataclass(frozen=True)
class _ReportCompositionResult:
    output: ReportGenerationOutput
    execution: PromptExecutionResult


class LLMReportComposer:
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

    def compose_report(
        self,
        job_results: list[JobAnalysisResult],
    ) -> _ReportCompositionResult:
        request = build_report_generation_prompt(
            job_results=job_results,
            model_name=self._model_name,
            temperature=self._temperature,
        )
        execution = self._llm_provider.execute_prompt(request)
        output = parse_structured_output(
            content=execution.content,
            schema=ReportGenerationOutput,
        )

        return _ReportCompositionResult(output=output, execution=execution)


class AnalysisReportGenerator:
    def __init__(
        self,
        *,
        requirement_extractor: DeterministicJobRequirementExtractor | None = None,
        evidence_retriever: ProfileEvidenceRetriever | None = None,
        requirement_matcher: DeterministicRequirementMatcher | None = None,
        scoring_service: RequirementScoringService | None = None,
        llm_provider: LLMProvider | None = None,
        llm_model_name: str | None = None,
        llm_temperature: float | None = None,
        llm_fallback_enabled: bool | None = None,
        retrieval_top_k: int = 3,
    ) -> None:
        if retrieval_top_k < 1:
            raise ValueError("retrieval_top_k must be greater than 0")

        settings = get_settings()
        resolved_llm_provider = (
            llm_provider
            if llm_provider is not None
            else (
                build_groq_llm_provider(settings)
                if settings.llm_provider == "groq"
                else None
            )
        )
        resolved_model_name = llm_model_name or settings.groq_model
        resolved_temperature = (
            llm_temperature
            if llm_temperature is not None
            else settings.groq_temperature
        )

        self._requirement_extractor = (
            requirement_extractor or DeterministicJobRequirementExtractor()
        )
        self._evidence_retriever = (
            evidence_retriever or SnapshotProfileEvidenceRetriever()
        )
        self._requirement_matcher = (
            requirement_matcher or DeterministicRequirementMatcher()
        )
        self._scoring_service = scoring_service or RequirementScoringService()
        self._retrieval_top_k = retrieval_top_k
        self._llm_fallback_enabled = (
            llm_fallback_enabled
            if llm_fallback_enabled is not None
            else settings.llm_deterministic_fallback_enabled
        )
        self._llm_requirement_extractor = (
            LLMJobRequirementExtractor(
                llm_provider=resolved_llm_provider,
                model_name=resolved_model_name,
                temperature=resolved_temperature,
            )
            if resolved_llm_provider is not None
            else None
        )
        self._llm_requirement_matcher = (
            LLMRequirementMatcher(
                llm_provider=resolved_llm_provider,
                model_name=resolved_model_name,
                temperature=resolved_temperature,
            )
            if resolved_llm_provider is not None
            else None
        )
        self._llm_report_composer = (
            LLMReportComposer(
                llm_provider=resolved_llm_provider,
                model_name=resolved_model_name,
                temperature=resolved_temperature,
            )
            if resolved_llm_provider is not None
            else None
        )

    def generate_report(
        self,
        context: AnalysisPipelineContext,
    ) -> AnalysisReportPackage:
        drafts = [
            self._analyze_job(context=context, job=job)
            for job in context.jobs
        ]
        ranked_drafts = sorted(
            drafts,
            key=lambda draft: (-draft.fit_score, draft.job.displayOrder),
        )
        job_results = [
            _build_job_result(draft=draft, rank_order=rank_order)
            for rank_order, draft in enumerate(ranked_drafts, start=1)
        ]
        report_summary, report_content, job_results = self._compose_report(
            context=context,
            job_results=job_results,
        )

        return AnalysisReportPackage(
            diagnosisId=context.diagnosisId,
            taskId=context.taskId,
            reportSummary=report_summary,
            reportContent=report_content,
            jobs=job_results,
        )

    def _analyze_job(
        self,
        *,
        context: AnalysisPipelineContext,
        job: AnalysisJobPosting,
    ) -> _JobAnalysisDraft:
        requirements = self._extract_requirements(context=context, job=job)
        requirement_matches = []

        for requirement in requirements:
            evidence = self._evidence_retriever.retrieve_evidence(
                diagnosis_id=context.diagnosisId,
                profile_snapshot=context.profileSnapshot,
                requirement=requirement,
                top_k=self._retrieval_top_k,
            )
            requirement_matches.append(
                self._match_requirement(
                    context=context,
                    job=job,
                    requirement=requirement,
                    evidence=evidence,
                )
            )

        return _JobAnalysisDraft(
            job=job,
            fit_score=self._scoring_service.calculate_fit_score(requirement_matches),
            requirement_matches=requirement_matches,
        )

    def _extract_requirements(
        self,
        *,
        context: AnalysisPipelineContext,
        job: AnalysisJobPosting,
    ) -> list[JobRequirement]:
        if self._llm_requirement_extractor is None:
            _record_deterministic_step(
                context.metadata,
                PipelineStep.JOB_STRUCTURING,
                fallback_used=True,
            )
            return self._requirement_extractor.extract_requirements(job)

        try:
            result = self._llm_requirement_extractor.extract_requirements(job)
        except LLMExecutionError:
            if not self._llm_fallback_enabled:
                raise
            _record_deterministic_step(
                context.metadata,
                PipelineStep.JOB_STRUCTURING,
                fallback_used=True,
            )
            return self._requirement_extractor.extract_requirements(job)

        _record_prompt_execution(
            context.metadata,
            step=PipelineStep.JOB_STRUCTURING,
            execution=result.execution,
        )
        return result.requirements

    def _match_requirement(
        self,
        *,
        context: AnalysisPipelineContext,
        job: AnalysisJobPosting,
        requirement: JobRequirement,
        evidence: list[MatchedProfileEvidence],
    ) -> RequirementMatch:
        if self._llm_requirement_matcher is None:
            _record_deterministic_step(
                context.metadata,
                PipelineStep.REQUIREMENT_MATCHING,
                fallback_used=True,
            )
            return self._requirement_matcher.match_requirement(
                requirement=requirement,
                evidence=evidence,
            )

        try:
            result = self._llm_requirement_matcher.match_requirement(
                job=job,
                requirement=requirement,
                evidence=evidence,
            )
        except LLMExecutionError:
            if not self._llm_fallback_enabled:
                raise
            _record_deterministic_step(
                context.metadata,
                PipelineStep.REQUIREMENT_MATCHING,
                fallback_used=True,
            )
            return self._requirement_matcher.match_requirement(
                requirement=requirement,
                evidence=evidence,
            )

        _record_prompt_execution(
            context.metadata,
            step=PipelineStep.REQUIREMENT_MATCHING,
            execution=result.execution,
        )
        return result.match

    def _compose_report(
        self,
        *,
        context: AnalysisPipelineContext,
        job_results: list[JobAnalysisResult],
    ) -> tuple[str, str, list[JobAnalysisResult]]:
        if self._llm_report_composer is None:
            _record_deterministic_step(
                context.metadata,
                PipelineStep.REPORT_GENERATION,
                fallback_used=True,
            )
            return (
                _build_report_summary(job_results),
                _build_report_content(job_results),
                job_results,
            )

        try:
            result = self._llm_report_composer.compose_report(job_results)
        except LLMExecutionError:
            if not self._llm_fallback_enabled:
                raise
            _record_deterministic_step(
                context.metadata,
                PipelineStep.REPORT_GENERATION,
                fallback_used=True,
            )
            return (
                _build_report_summary(job_results),
                _build_report_content(job_results),
                job_results,
            )

        _record_prompt_execution(
            context.metadata,
            step=PipelineStep.REPORT_GENERATION,
            execution=result.execution,
        )
        return (
            result.output.reportSummary,
            result.output.reportContent,
            _apply_report_generation_output(
                job_results=job_results,
                output=result.output,
            ),
        )


def _apply_report_generation_output(
    *,
    job_results: list[JobAnalysisResult],
    output: ReportGenerationOutput,
) -> list[JobAnalysisResult]:
    summaries_by_jd_id = {summary.jdId: summary for summary in output.jobs}
    updated_results = []

    for job in job_results:
        summary = summaries_by_jd_id.get(job.jdId)
        if summary is None:
            updated_results.append(job)
            continue

        updated_results.append(
            job.model_copy(
                update={
                    "strengthsSummary": summary.strengthsSummary
                    or job.strengthsSummary,
                    "gapsSummary": summary.gapsSummary or job.gapsSummary,
                    "highlightPoints": summary.highlightPoints
                    or job.highlightPoints,
                }
            )
        )

    return updated_results


def _record_prompt_execution(
    metadata: AnalysisMetadata,
    *,
    step: PipelineStep,
    execution: PromptExecutionResult,
) -> None:
    _merge_step_metadata(
        metadata,
        step=step,
        model_name=execution.modelName,
        prompt_version=execution.promptVersion,
        provider_name=execution.providerName,
        duration_ms=execution.durationMs,
        retry_count=execution.retryCount,
        fallback_used=False,
    )


def _record_deterministic_step(
    metadata: AnalysisMetadata,
    step: PipelineStep,
    *,
    fallback_used: bool,
) -> None:
    _merge_step_metadata(
        metadata,
        step=step,
        model_name="deterministic",
        prompt_version=None,
        provider_name="deterministic",
        duration_ms=None,
        retry_count=None,
        fallback_used=fallback_used,
    )


def _merge_step_metadata(
    metadata: AnalysisMetadata,
    *,
    step: PipelineStep,
    model_name: str | None,
    prompt_version: str | None,
    provider_name: str | None,
    duration_ms: int | None,
    retry_count: int | None,
    fallback_used: bool,
) -> None:
    existing = metadata.steps.get(step.value)
    metadata.steps[step.value] = AnalysisStepMetadata(
        step=step.value,
        modelName=model_name or (existing.modelName if existing else None),
        promptVersion=prompt_version or (existing.promptVersion if existing else None),
        providerName=provider_name or (existing.providerName if existing else None),
        durationMs=_sum_optional(existing.durationMs if existing else None, duration_ms),
        retryCount=_sum_optional(existing.retryCount if existing else None, retry_count),
        fallbackUsed=fallback_used or bool(existing.fallbackUsed if existing else False),
    )


def _sum_optional(left: int | None, right: int | None) -> int | None:
    if left is None:
        return right
    if right is None:
        return left
    return left + right


def _build_job_result(
    *,
    draft: _JobAnalysisDraft,
    rank_order: int,
) -> JobAnalysisResult:
    return JobAnalysisResult(
        jdId=draft.job.jdId,
        rankOrder=rank_order,
        companyName=draft.job.companyName,
        position=draft.job.position,
        fitScore=draft.fit_score,
        strengthsSummary=_build_strengths_summary(draft.requirement_matches),
        gapsSummary=_build_gaps_summary(draft.requirement_matches),
        highlightPoints=_build_highlight_points(draft.requirement_matches),
        requirementMatches=draft.requirement_matches,
    )


def _build_strengths_summary(matches: list[RequirementMatch]) -> str:
    matched_descriptions = [
        match.requirement.description
        for match in matches
        if match.status == "matched"
    ]
    if not matched_descriptions:
        return "명확히 충족된 요구사항이 아직 부족합니다."

    return "충족 요구사항: " + "; ".join(matched_descriptions[:3])


def _build_gaps_summary(matches: list[RequirementMatch]) -> str:
    gap_descriptions = [
        match.requirement.description
        for match in matches
        if match.status in {"partial", "missing"}
    ]
    if not gap_descriptions:
        return "주요 부족 요소가 적습니다."

    return "보완 필요: " + "; ".join(gap_descriptions[:3])


def _build_highlight_points(matches: list[RequirementMatch]) -> list[str]:
    highlights = []
    for match in matches:
        if match.status == "missing":
            continue
        for keyword in match.requirement.keywords:
            if keyword not in highlights:
                highlights.append(keyword)
            if len(highlights) >= 5:
                return highlights

    return highlights


def _build_report_summary(job_results: list[JobAnalysisResult]) -> str:
    top_job = job_results[0]
    label = _format_job_label(top_job)
    if len(job_results) == 1:
        return f"{label} 공고의 적합도는 {top_job.fitScore}점입니다."

    return f"가장 적합한 공고는 {label}이며 적합도는 {top_job.fitScore}점입니다."


def _build_report_content(job_results: list[JobAnalysisResult]) -> str:
    lines = ["# AI 분석 리포트", "", "## 공고별 결과"]
    for job in job_results:
        lines.extend(
            [
                "",
                f"### {job.rankOrder}. {_format_job_label(job)}",
                f"- 적합도: {job.fitScore}점",
                f"- 강점: {job.strengthsSummary}",
                f"- 보완점: {job.gapsSummary}",
            ]
        )

    return "\n".join(lines)


def _format_job_label(job: JobAnalysisResult) -> str:
    if job.position:
        return f"{job.companyName} {job.position}"
    return job.companyName
