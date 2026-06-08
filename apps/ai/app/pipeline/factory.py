from __future__ import annotations

from app.core.config import Settings, get_settings
from app.pipeline.evidence_retrieval import (
    QdrantProfileEvidenceRetriever,
    ResilientProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.pipeline.orchestrator import AnalysisPipeline
from app.pipeline.reporting import AnalysisReportGenerator
from app.retrieval.embeddings import TextEmbeddingProvider
from app.retrieval.factory import (
    build_profile_snapshot_indexing_service,
    build_profile_vector_store,
)
from app.retrieval.sentence_transformers import SentenceTransformersEmbeddingProvider
from app.retrieval.vector_store import ProfileVectorStore


def build_default_analysis_pipeline(
    *,
    settings: Settings | None = None,
    embedding_provider: TextEmbeddingProvider | None = None,
    vector_store: ProfileVectorStore | None = None,
) -> AnalysisPipeline:
    resolved_settings = settings or get_settings()

    if resolved_settings.profile_retrieval_provider == "snapshot":
        return AnalysisPipeline()

    resolved_embedding_provider = embedding_provider or (
        SentenceTransformersEmbeddingProvider(
            model_name=resolved_settings.embedding_model,
        )
    )
    resolved_vector_store = vector_store or build_profile_vector_store(
        settings=resolved_settings,
    )
    indexing_service = build_profile_snapshot_indexing_service(
        embedding_provider=resolved_embedding_provider,
        settings=resolved_settings,
        vector_store=resolved_vector_store,
    )
    evidence_retriever = ResilientProfileEvidenceRetriever(
        primary=QdrantProfileEvidenceRetriever(
            embedding_provider=resolved_embedding_provider,
            vector_store=resolved_vector_store,
        ),
        fallback=SnapshotProfileEvidenceRetriever(),
    )

    return AnalysisPipeline(
        profile_indexer=indexing_service,
        profile_indexing_fallback_enabled=True,
        report_generator=AnalysisReportGenerator(
            evidence_retriever=evidence_retriever,
        ),
    )


__all__ = [
    "build_default_analysis_pipeline",
]
