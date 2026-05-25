from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.evidence_retrieval import (
    ProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.pipeline.job_structuring import DeterministicJobRequirementExtractor
from app.pipeline.matching import DeterministicRequirementMatcher
from app.pipeline.scoring import RequirementScoringService
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    AnalysisReportPackage,
    JobAnalysisResult,
    RequirementMatch,
)


@dataclass(frozen=True)
class _JobAnalysisDraft:
    job: AnalysisJobPosting
    fit_score: float
    requirement_matches: list[RequirementMatch]


class AnalysisReportGenerator:
    def __init__(
        self,
        *,
        requirement_extractor: DeterministicJobRequirementExtractor | None = None,
        evidence_retriever: ProfileEvidenceRetriever | None = None,
        requirement_matcher: DeterministicRequirementMatcher | None = None,
        scoring_service: RequirementScoringService | None = None,
        retrieval_top_k: int = 3,
    ) -> None:
        if retrieval_top_k < 1:
            raise ValueError("retrieval_top_k must be greater than 0")

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

        return AnalysisReportPackage(
            diagnosisId=context.diagnosisId,
            taskId=context.taskId,
            reportSummary=_build_report_summary(job_results),
            reportContent=_build_report_content(job_results),
            jobs=job_results,
        )

    def _analyze_job(
        self,
        *,
        context: AnalysisPipelineContext,
        job: AnalysisJobPosting,
    ) -> _JobAnalysisDraft:
        requirements = self._requirement_extractor.extract_requirements(job)
        requirement_matches = []

        for requirement in requirements:
            evidence = self._evidence_retriever.retrieve_evidence(
                diagnosis_id=context.diagnosisId,
                profile_snapshot=context.profileSnapshot,
                requirement=requirement,
                top_k=self._retrieval_top_k,
            )
            requirement_matches.append(
                self._requirement_matcher.match_requirement(
                    requirement=requirement,
                    evidence=evidence,
                )
            )

        return _JobAnalysisDraft(
            job=job,
            fit_score=self._scoring_service.calculate_fit_score(requirement_matches),
            requirement_matches=requirement_matches,
        )


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
