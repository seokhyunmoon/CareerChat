from __future__ import annotations

import uuid
from collections.abc import Sequence

from qdrant_client import models

from app.retrieval.chunks import ProfileSnapshotChunk

# Fixed namespace for deterministic Qdrant point IDs generated from profile chunk IDs.
PROFILE_CHUNK_POINT_NAMESPACE = uuid.UUID("7235791f-6d3e-4a34-83f7-0c2e94eb2d97")


def build_profile_chunk_point(
    chunk: ProfileSnapshotChunk,
    vector: Sequence[float],
) -> models.PointStruct:
    vector_values = _validate_vector(vector)
    return models.PointStruct(
        id=build_profile_chunk_point_id(chunk.chunk_id),
        vector=vector_values,
        payload=chunk.to_qdrant_payload().model_dump(),
    )


def build_profile_chunk_points(
    chunks: Sequence[ProfileSnapshotChunk],
    vectors: Sequence[Sequence[float]],
) -> list[models.PointStruct]:
    if len(chunks) != len(vectors):
        raise ValueError("chunks and vectors must have the same length")

    return [
        build_profile_chunk_point(chunk, vector)
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]


def build_profile_chunk_point_id(chunk_id: str) -> str:
    if not chunk_id.strip():
        raise ValueError("chunk_id must not be blank")
    return str(uuid.uuid5(PROFILE_CHUNK_POINT_NAMESPACE, chunk_id))


def _validate_vector(vector: Sequence[float]) -> list[float]:
    vector_values = [float(value) for value in vector]
    if not vector_values:
        raise ValueError("vector must not be empty")
    return vector_values
