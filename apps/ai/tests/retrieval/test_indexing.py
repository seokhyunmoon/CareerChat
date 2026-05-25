from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import pytest
from qdrant_client import models

from app.retrieval import ProfileSnapshotIndexingService


def test_index_profile_snapshot_chunks_embeds_and_upserts_points() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    service = ProfileSnapshotIndexingService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = service.index_profile_snapshot(
        diagnosis_id=1,
        payload=_valid_payload(),
    )

    assert [chunk.chunk_id for chunk in chunks] == [
        "diagnosis-1-profile_overview-10-0",
        "diagnosis-1-project-3-0",
    ]
    assert embedding_provider.texts == [
        "프로필 요약. 경력 수준: junior.",
        "프로젝트명: CareerChat. 설명: React 프로젝트.",
    ]
    assert vector_store.calls == ["ensure_collection", "upsert_profile_chunks"]
    assert vector_store.points is not None
    assert [point.payload["chunkId"] for point in vector_store.points] == [
        "diagnosis-1-profile_overview-10-0",
        "diagnosis-1-project-3-0",
    ]


def test_index_profile_snapshot_rejects_embedding_vector_count_mismatch() -> None:
    service = ProfileSnapshotIndexingService(
        embedding_provider=FakeEmbeddingProvider(vectors=[[0.1, 0.2, 0.3]]),
        vector_store=FakeVectorStore(),
    )

    with pytest.raises(ValueError, match="same length"):
        service.index_profile_snapshot(
            diagnosis_id=1,
            payload=_valid_payload(),
        )


def test_index_profile_snapshot_does_not_embed_or_upsert_invalid_payload() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    service = ProfileSnapshotIndexingService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )
    payload = _valid_payload()
    payload["projects"][0]["email"] = "user@example.com"

    with pytest.raises(ValueError, match="PII keys: email"):
        service.index_profile_snapshot(diagnosis_id=1, payload=payload)

    assert embedding_provider.texts is None
    assert vector_store.calls == []
    assert vector_store.points is None


@dataclass
class FakeEmbeddingProvider:
    vectors: list[list[float]] | None = None
    texts: list[str] | None = None

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        self.texts = list(texts)
        if self.vectors is not None:
            return self.vectors
        return [[float(index), 0.1, 0.2] for index, _ in enumerate(texts)]


@dataclass
class FakeVectorStore:
    calls: list[str] = field(default_factory=list)
    points: list[models.PointStruct] | None = None

    def ensure_collection(self) -> None:
        self.calls.append("ensure_collection")

    def upsert_profile_chunks(self, points: Sequence[models.PointStruct]) -> None:
        self.calls.append("upsert_profile_chunks")
        self.points = list(points)


def _valid_payload() -> dict:
    return {
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
                "description": "React 프로젝트",
            }
        ],
        "achievements": [],
    }
