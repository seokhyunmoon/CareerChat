from __future__ import annotations

from typing import Any, Protocol

from app.pipeline.deterministic_text import calculate_term_relevance, extract_match_terms
from app.retrieval.chunks import QdrantProfileChunkPayload
from app.retrieval.chunking import build_profile_snapshot_chunks
from app.retrieval.embeddings import TextEmbeddingProvider
from app.schemas.analysis_result import JobRequirement, MatchedProfileEvidence
from app.schemas.profile_snapshot import ProfileSnapshot


class ProfileEvidenceRetriever(Protocol):
    def retrieve_evidence(
        self,
        *,
        diagnosis_id: int,
        profile_snapshot: ProfileSnapshot,
        requirement: JobRequirement,
        top_k: int,
    ) -> list[MatchedProfileEvidence]: ...


class ProfileChunkSearcher(Protocol):
    def search_profile_chunks(
        self,
        *,
        diagnosis_id: int,
        query_vector: list[float],
        limit: int,
    ) -> list[Any]: ...


class QdrantProfileEvidenceRetriever:
    provider_name = "qdrant"

    def __init__(
        self,
        *,
        embedding_provider: TextEmbeddingProvider,
        vector_store: ProfileChunkSearcher,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def retrieve_evidence(
        self,
        *,
        diagnosis_id: int,
        profile_snapshot: ProfileSnapshot,
        requirement: JobRequirement,
        top_k: int = 3,
    ) -> list[MatchedProfileEvidence]:
        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        query_text = _build_requirement_query_text(requirement)
        query_vector = self._embedding_provider.embed_texts([query_text])[0]
        scored_points = self._vector_store.search_profile_chunks(
            diagnosis_id=diagnosis_id,
            query_vector=query_vector,
            limit=top_k,
        )

        return [
            _build_evidence_from_scored_point(scored_point)
            for scored_point in scored_points
            if getattr(scored_point, "payload", None)
        ]


class SnapshotProfileEvidenceRetriever:
    provider_name = "snapshot"

    def retrieve_evidence(
        self,
        *,
        diagnosis_id: int,
        profile_snapshot: ProfileSnapshot,
        requirement: JobRequirement,
        top_k: int = 3,
    ) -> list[MatchedProfileEvidence]:
        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        query_terms = extract_match_terms(
            requirement.description,
            *requirement.keywords,
        )
        chunks = build_profile_snapshot_chunks(
            diagnosis_id=diagnosis_id,
            snapshot=profile_snapshot,
        )

        scored_chunks = []
        for chunk in chunks:
            relevance_score = calculate_term_relevance(query_terms, chunk.text)
            if relevance_score <= 0:
                continue
            scored_chunks.append((relevance_score, chunk.chunk_id, chunk))

        scored_chunks.sort(key=lambda item: (-item[0], item[1]))

        return [
            MatchedProfileEvidence(
                evidence=chunk.evidence,
                relevanceScore=round(relevance_score, 4),
                rationale="프로필 snapshot 근거가 요구사항 키워드와 일치합니다.",
            )
            for relevance_score, _, chunk in scored_chunks[:top_k]
        ]


def _build_requirement_query_text(requirement: JobRequirement) -> str:
    parts = [requirement.description, *requirement.keywords]
    return " ".join(part for part in parts if part)


def _build_evidence_from_scored_point(scored_point: Any) -> MatchedProfileEvidence:
    payload = QdrantProfileChunkPayload.model_validate(scored_point.payload)

    return MatchedProfileEvidence(
        evidence={
            "sourceType": payload.sourceType,
            "sourceId": payload.sourceId,
            "chunkIndex": payload.chunkIndex,
            "title": payload.title,
            "text": payload.text,
        },
        relevanceScore=round(float(scored_point.score), 4),
        rationale="Qdrant profile evidence matched the requirement query.",
    )


class ResilientProfileEvidenceRetriever:
    provider_name = "qdrant_with_snapshot_fallback"

    def __init__(
        self,
        *,
        primary: ProfileEvidenceRetriever,
        fallback: ProfileEvidenceRetriever,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self.last_provider_name = getattr(primary, "provider_name", "primary")
        self.last_fallback_used = False

    def retrieve_evidence(
        self,
        *,
        diagnosis_id: int,
        profile_snapshot: ProfileSnapshot,
        requirement: JobRequirement,
        top_k: int,
    ) -> list[MatchedProfileEvidence]:
        self.last_provider_name = getattr(self._primary, "provider_name", "primary")
        self.last_fallback_used = False

        try:
            return self._primary.retrieve_evidence(
                diagnosis_id=diagnosis_id,
                profile_snapshot=profile_snapshot,
                requirement=requirement,
                top_k=top_k,
            )
        except Exception:
            self.last_provider_name = getattr(
                self._fallback,
                "provider_name",
                "fallback",
            )
            self.last_fallback_used = True
            return self._fallback.retrieve_evidence(
                diagnosis_id=diagnosis_id,
                profile_snapshot=profile_snapshot,
                requirement=requirement,
                top_k=top_k,
            )
