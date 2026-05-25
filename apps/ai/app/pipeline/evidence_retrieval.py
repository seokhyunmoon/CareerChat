from __future__ import annotations

from typing import Protocol

from app.pipeline.deterministic_text import calculate_term_relevance, extract_match_terms
from app.retrieval.chunking import build_profile_snapshot_chunks
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


class SnapshotProfileEvidenceRetriever:
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
