"""Analysis orchestration package for the AI backend foundation."""

from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.evidence_retrieval import (
    ProfileEvidenceRetriever,
    QdrantProfileEvidenceRetriever,
    ResilientProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.pipeline.factory import build_default_analysis_pipeline
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
    "ResilientProfileEvidenceRetriever",
    "RequirementScoringService",
    "SnapshotProfileEvidenceRetriever",
    "build_default_analysis_pipeline",
]
