from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from qdrant_client import models

from app.core.config import Settings
from app.retrieval import (
    build_default_profile_snapshot_indexing_service,
    build_profile_snapshot_indexing_service,
    build_profile_vector_store,
)


def test_build_profile_vector_store_uses_settings_and_injected_client() -> None:
    client = FakeQdrantClient()

    store = build_profile_vector_store(
        settings=Settings(
            qdrant_collection_name="test_profile_chunks",
            qdrant_vector_size=768,
        ),
        client=client,
    )

    store.ensure_collection()

    assert client.created_collection == {
        "collection_name": "test_profile_chunks",
        "size": 768,
        "distance": models.Distance.COSINE,
    }


def test_build_profile_snapshot_indexing_service_uses_injected_dependencies() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()

    service = build_profile_snapshot_indexing_service(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chunks = service.index_profile_snapshot(
        diagnosis_id=1,
        payload={
            "snapshotVersion": 1,
            "profile": {
                "profileId": 10,
                "experienceLevel": "junior",
            },
            "education": [],
            "workExperiences": [],
            "projects": [],
            "achievements": [],
        },
    )

    assert [chunk.chunk_id for chunk in chunks] == [
        "diagnosis-1-profile_overview-10-0"
    ]
    assert embedding_provider.texts == ["프로필 요약. 경력 수준: junior."]
    assert vector_store.ensure_collection_called is True
    assert vector_store.points is not None
    assert vector_store.points[0].payload["chunkId"] == (
        "diagnosis-1-profile_overview-10-0"
    )


def test_build_default_profile_snapshot_indexing_service_uses_settings_model_name() -> None:
    vector_store = FakeVectorStore()

    service = build_default_profile_snapshot_indexing_service(
        settings=Settings(
            embedding_model="sentence-transformers/test-model",
        ),
        vector_store=vector_store,
    )

    assert service is not None


@dataclass
class FakeEmbeddingProvider:
    texts: list[str] | None = None

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        self.texts = list(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]


@dataclass
class FakeVectorStore:
    ensure_collection_called: bool = False
    points: list[models.PointStruct] | None = None

    def ensure_collection(self) -> None:
        self.ensure_collection_called = True

    def upsert_profile_chunks(self, points: Sequence[models.PointStruct]) -> None:
        self.points = list(points)


@dataclass
class FakeQdrantClient:
    created_collection: dict | None = None
    created_payload_index: dict | None = None

    def collection_exists(self, collection_name: str) -> bool:
        return False

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
        points: Sequence[models.PointStruct],
        wait: bool = True,
    ) -> object:
        return object()

    def query_points(
        self,
        collection_name: str,
        query: list[float],
        query_filter: models.Filter,
        limit: int,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> object:
        return object()
