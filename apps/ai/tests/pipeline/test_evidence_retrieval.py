from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.pipeline.evidence_retrieval import (
    QdrantProfileEvidenceRetriever,
    SnapshotProfileEvidenceRetriever,
)
from app.schemas.analysis_result import JobRequirement
from app.schemas.profile_snapshot import ProfileSnapshot


def build_profile_snapshot() -> ProfileSnapshot:
    return ProfileSnapshot.model_validate(
        {
            "snapshotVersion": 1,
            "profile": {
                "profileId": 10,
                "experienceLevel": "junior",
            },
            "education": [],
            "workExperiences": [],
            "projects": [
                {
                    "projectId": 3,
                    "projectName": "CareerChat",
                    "description": "Spring Boot 기반 REST API와 Redis 작업 큐를 구현했습니다.",
                }
            ],
            "achievements": [],
        }
    )


def test_snapshot_profile_evidence_retriever_returns_relevant_profile_chunks() -> None:
    requirement = JobRequirement(
        requirementId="req-1",
        category="skill",
        priority="required",
        description="Spring Boot REST API 개발 경험",
        keywords=["spring boot", "rest api"],
    )

    evidence = SnapshotProfileEvidenceRetriever().retrieve_evidence(
        diagnosis_id=1,
        profile_snapshot=build_profile_snapshot(),
        requirement=requirement,
        top_k=2,
    )

    assert len(evidence) == 1
    assert evidence[0].evidence.sourceType == "project"
    assert evidence[0].evidence.sourceId == 3
    assert evidence[0].relevanceScore > 0.5


def test_snapshot_profile_evidence_retriever_rejects_invalid_top_k() -> None:
    requirement = JobRequirement(
        requirementId="req-1",
        description="Spring Boot REST API 개발 경험",
    )

    with pytest.raises(ValueError, match="top_k"):
        SnapshotProfileEvidenceRetriever().retrieve_evidence(
            diagnosis_id=1,
            profile_snapshot=build_profile_snapshot(),
            requirement=requirement,
            top_k=0,
        )


def test_qdrant_profile_evidence_retriever_searches_with_embedding_vector() -> None:
    embedding_provider = FakeEmbeddingProvider(vector=[0.1, 0.2, 0.3])
    vector_store = FakeVectorStore(
        scored_points=[
            FakeScoredPoint(
                score=0.87654,
                payload={
                    "diagnosisId": 1,
                    "chunkId": "diagnosis-1-project-3-0",
                    "sourceType": "project",
                    "sourceId": 3,
                    "chunkIndex": 0,
                    "title": "CareerChat",
                    "text": "Spring Boot REST API와 Redis 작업 큐를 구현했습니다.",
                    "metadata": {"snapshotVersion": 1},
                },
            )
        ]
    )
    requirement = JobRequirement(
        requirementId="req-1",
        category="skill",
        priority="required",
        description="Spring Boot REST API 개발 경험",
        keywords=["spring boot", "rest api"],
    )

    evidence = QdrantProfileEvidenceRetriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    ).retrieve_evidence(
        diagnosis_id=1,
        profile_snapshot=build_profile_snapshot(),
        requirement=requirement,
        top_k=2,
    )

    assert embedding_provider.texts == [
        "Spring Boot REST API 개발 경험 spring boot rest api"
    ]
    assert vector_store.search_kwargs == {
        "diagnosis_id": 1,
        "query_vector": [0.1, 0.2, 0.3],
        "limit": 2,
    }
    assert len(evidence) == 1
    assert evidence[0].evidence.sourceType == "project"
    assert evidence[0].evidence.sourceId == 3
    assert evidence[0].relevanceScore == 0.8765


def test_qdrant_profile_evidence_retriever_rejects_invalid_top_k() -> None:
    requirement = JobRequirement(
        requirementId="req-1",
        description="Spring Boot REST API 개발 경험",
    )

    with pytest.raises(ValueError, match="top_k"):
        QdrantProfileEvidenceRetriever(
            embedding_provider=FakeEmbeddingProvider(vector=[0.1]),
            vector_store=FakeVectorStore(scored_points=[]),
        ).retrieve_evidence(
            diagnosis_id=1,
            profile_snapshot=build_profile_snapshot(),
            requirement=requirement,
            top_k=0,
        )


class FakeEmbeddingProvider:
    def __init__(self, vector: list[float]) -> None:
        self._vector = vector
        self.texts: list[str] | None = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.texts = texts
        return [self._vector for _ in texts]


class FakeVectorStore:
    def __init__(self, scored_points: list["FakeScoredPoint"]) -> None:
        self._scored_points = scored_points
        self.search_kwargs: dict | None = None

    def search_profile_chunks(
        self,
        *,
        diagnosis_id: int,
        query_vector: list[float],
        limit: int,
    ) -> list["FakeScoredPoint"]:
        self.search_kwargs = {
            "diagnosis_id": diagnosis_id,
            "query_vector": query_vector,
            "limit": limit,
        }
        return self._scored_points


@dataclass
class FakeScoredPoint:
    score: float
    payload: dict
