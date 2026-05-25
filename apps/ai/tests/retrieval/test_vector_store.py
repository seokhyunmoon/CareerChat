from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from qdrant_client import models

from app.retrieval import ProfileVectorStore, build_profile_chunk_point
from app.retrieval.chunks import ProfileSnapshotChunk
from app.schemas.profile_snapshot import ProfileEvidenceReference


def test_ensure_collection_creates_collection_and_diagnosis_payload_index() -> None:
    client = FakeQdrantClient(collection_already_exists=False)
    store = ProfileVectorStore(
        client=client,
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )

    store.ensure_collection()

    assert client.created_collection == {
        "collection_name": "careerchat_profile_chunks",
        "size": 384,
        "distance": models.Distance.COSINE,
    }
    assert client.created_payload_index == {
        "collection_name": "careerchat_profile_chunks",
        "field_name": "diagnosisId",
        "field_schema": models.PayloadSchemaType.INTEGER,
    }


def test_ensure_collection_skips_creation_when_collection_exists() -> None:
    client = FakeQdrantClient(collection_already_exists=True)
    store = ProfileVectorStore(
        client=client,
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )

    store.ensure_collection()

    assert client.created_collection is None
    assert client.created_payload_index is None


def test_upsert_profile_chunks_passes_points_to_qdrant() -> None:
    client = FakeQdrantClient(collection_already_exists=True)
    store = ProfileVectorStore(
        client=client,
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )
    point = build_profile_chunk_point(_build_chunk(), [0.1, 0.2, 0.3])

    store.upsert_profile_chunks([point])

    assert client.upserted_points == [point]
    assert client.upsert_wait is True


def test_upsert_profile_chunks_skips_empty_points() -> None:
    client = FakeQdrantClient(collection_already_exists=True)
    store = ProfileVectorStore(
        client=client,
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )

    store.upsert_profile_chunks([])

    assert client.upserted_points is None


def test_search_profile_chunks_forces_diagnosis_filter() -> None:
    scored_point = models.ScoredPoint(
        id="550e8400-e29b-41d4-a716-446655440000",
        version=1,
        score=0.9,
        payload={"diagnosisId": 1},
    )
    client = FakeQdrantClient(
        collection_already_exists=True,
        query_response=FakeQueryResponse(points=[scored_point]),
    )
    store = ProfileVectorStore(
        client=client,
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )

    results = store.search_profile_chunks(
        diagnosis_id=1,
        query_vector=[0.1, 0.2, 0.3],
        limit=5,
    )

    assert results == [scored_point]
    assert client.query_kwargs is not None
    assert client.query_kwargs["collection_name"] == "careerchat_profile_chunks"
    assert client.query_kwargs["query"] == [0.1, 0.2, 0.3]
    assert client.query_kwargs["limit"] == 5
    assert client.query_kwargs["with_payload"] is True
    assert client.query_kwargs["with_vectors"] is False

    query_filter = client.query_kwargs["query_filter"]
    assert query_filter.must[0].key == "diagnosisId"
    assert query_filter.must[0].match.value == 1


@pytest.mark.parametrize(
    ("collection_name", "vector_size", "error_message"),
    [
        (" ", 384, "collection_name must not be blank"),
        ("careerchat_profile_chunks", 0, "vector_size must be greater than 0"),
    ],
)
def test_profile_vector_store_rejects_invalid_constructor_values(
    collection_name: str,
    vector_size: int,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        ProfileVectorStore(
            client=FakeQdrantClient(collection_already_exists=True),
            collection_name=collection_name,
            vector_size=vector_size,
        )


@pytest.mark.parametrize(
    ("query_vector", "limit", "error_message"),
    [
        ([], 5, "query_vector must not be empty"),
        ([0.1, 0.2], 0, "limit must be greater than 0"),
    ],
)
def test_search_profile_chunks_rejects_invalid_search_values(
    query_vector: list[float],
    limit: int,
    error_message: str,
) -> None:
    store = ProfileVectorStore(
        client=FakeQdrantClient(collection_already_exists=True),
        collection_name="careerchat_profile_chunks",
        vector_size=384,
    )

    with pytest.raises(ValueError, match=error_message):
        store.search_profile_chunks(
            diagnosis_id=1,
            query_vector=query_vector,
            limit=limit,
        )


@dataclass
class FakeQueryResponse:
    points: list[models.ScoredPoint]


@dataclass
class FakeQdrantClient:
    collection_already_exists: bool
    query_response: FakeQueryResponse = field(
        default_factory=lambda: FakeQueryResponse([])
    )
    created_collection: dict[str, Any] | None = None
    created_payload_index: dict[str, Any] | None = None
    upserted_points: list[models.PointStruct] | None = None
    upsert_wait: bool | None = None
    query_kwargs: dict[str, Any] | None = None

    def collection_exists(self, collection_name: str) -> bool:
        return self.collection_already_exists

    def create_collection(
        self,
        collection_name: str,
        vectors_config: models.VectorParams,
    ) -> bool:
        self.created_collection = {
            "collection_name": collection_name,
            "size": vectors_config.size,
            "distance": vectors_config.distance,
        }
        return True

    def create_payload_index(
        self,
        collection_name: str,
        field_name: str,
        field_schema: models.PayloadSchemaType,
    ) -> object:
        self.created_payload_index = {
            "collection_name": collection_name,
            "field_name": field_name,
            "field_schema": field_schema,
        }
        return object()

    def upsert(
        self,
        collection_name: str,
        points: list[models.PointStruct],
        wait: bool = True,
    ) -> object:
        self.upserted_points = points
        self.upsert_wait = wait
        return object()

    def query_points(
        self,
        collection_name: str,
        query: list[float],
        query_filter: models.Filter,
        limit: int,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> FakeQueryResponse:
        self.query_kwargs = {
            "collection_name": collection_name,
            "query": query,
            "query_filter": query_filter,
            "limit": limit,
            "with_payload": with_payload,
            "with_vectors": with_vectors,
        }
        return self.query_response


def _build_chunk() -> ProfileSnapshotChunk:
    return ProfileSnapshotChunk(
        diagnosis_id=1,
        chunk_id="diagnosis-1-project-3-0",
        text="프로젝트명: CareerChat. 설명: React 프로젝트.",
        evidence=ProfileEvidenceReference(
            sourceType="project",
            sourceId=3,
            chunkIndex=0,
            title="CareerChat",
            text="프로젝트명: CareerChat. 설명: React 프로젝트.",
        ),
        metadata={"snapshotVersion": 1},
    )
