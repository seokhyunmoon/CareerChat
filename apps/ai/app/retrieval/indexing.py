from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from qdrant_client import models

from app.retrieval.chunking import build_safe_profile_snapshot_chunks
from app.retrieval.chunks import ProfileSnapshotChunk
from app.retrieval.embeddings import TextEmbeddingProvider
from app.retrieval.points import build_profile_chunk_points


class ProfileVectorStoreWriter(Protocol):
    def ensure_collection(self) -> None: ...

    def upsert_profile_chunks(self, points: Sequence[models.PointStruct]) -> None: ...


class ProfileSnapshotIndexingService:
    def __init__(
        self,
        *,
        embedding_provider: TextEmbeddingProvider,
        vector_store: ProfileVectorStoreWriter,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def index_profile_snapshot(
        self,
        *,
        diagnosis_id: int,
        payload: dict[str, Any],
    ) -> list[ProfileSnapshotChunk]:
        chunks = build_safe_profile_snapshot_chunks(
            diagnosis_id=diagnosis_id,
            payload=payload,
        )
        if not chunks:
            return []

        vectors = self._embedding_provider.embed_texts(
            [chunk.text for chunk in chunks]
        )
        points = build_profile_chunk_points(chunks, vectors)

        self._vector_store.ensure_collection()
        self._vector_store.upsert_profile_chunks(points)

        return chunks
