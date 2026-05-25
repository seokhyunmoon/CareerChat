from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from qdrant_client import models

from app.retrieval.filters import build_diagnosis_filter


class QdrantProfileClient(Protocol):
    def collection_exists(self, collection_name: str) -> bool: ...

    def create_collection(
        self,
        collection_name: str,
        vectors_config: models.VectorParams,
    ) -> bool: ...

    def create_payload_index(
        self,
        collection_name: str,
        field_name: str,
        field_schema: models.PayloadSchemaType,
    ) -> object: ...

    def upsert(
        self,
        collection_name: str,
        points: Sequence[models.PointStruct],
        wait: bool = True,
    ) -> object: ...

    def query_points(
        self,
        collection_name: str,
        query: list[float],
        query_filter: models.Filter,
        limit: int,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> object: ...


class ProfileVectorStore:
    def __init__(
        self,
        *,
        client: QdrantProfileClient,
        collection_name: str,
        vector_size: int,
    ) -> None:
        if not collection_name.strip():
            raise ValueError("collection_name must not be blank")
        if vector_size < 1:
            raise ValueError("vector_size must be greater than 0")

        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=models.VectorParams(
                size=self._vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        self._client.create_payload_index(
            collection_name=self._collection_name,
            field_name="diagnosisId",
            field_schema=models.PayloadSchemaType.INTEGER,
        )

    def upsert_profile_chunks(self, points: Sequence[models.PointStruct]) -> None:
        if not points:
            return

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
            wait=True,
        )

    def search_profile_chunks(
        self,
        *,
        diagnosis_id: int,
        query_vector: Sequence[float],
        limit: int,
    ) -> list[models.ScoredPoint]:
        if limit < 1:
            raise ValueError("limit must be greater than 0")

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=_normalize_vector(query_vector),
            query_filter=build_diagnosis_filter(diagnosis_id),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return list(getattr(response, "points", []))


def _normalize_vector(vector: Sequence[float]) -> list[float]:
    values = [float(value) for value in vector]
    if not values:
        raise ValueError("query_vector must not be empty")
    return values
