"""Analysis orchestration package for the AI backend foundation."""

from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.evidence_retrieval import (
    ProfileEvidenceRetriever,
    QdrantProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.pipeline.job_structuring import (
    DeterministicJobRequirementExtractor,
    LLMJobRequirementExtractor,
)
from app.pipeline.matching import DeterministicRequirementMatcher, LLMRequirementMatcher
from app.pipeline.orchestrator import AnalysisPipeline
from app.pipeline.reporting import AnalysisReportGenerator, LLMReportComposer
from app.pipeline.scoring import RequirementScoringService

__all__ = [
    "AnalysisPipeline",
    "AnalysisPipelineContext",
    "AnalysisPipelineResult",
    "AnalysisReportGenerator",
    "DeterministicJobRequirementExtractor",
    "DeterministicRequirementMatcher",
    "LLMJobRequirementExtractor",
    "LLMReportComposer",
    "LLMRequirementMatcher",
    "ProfileEvidenceRetriever",
    "QdrantProfileEvidenceRetriever",
    "RequirementScoringService",
    "SnapshotProfileEvidenceRetriever",
]
