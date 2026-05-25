from __future__ import annotations

import uuid

import pytest

from app.retrieval import (
    build_profile_chunk_point,
    build_profile_chunk_point_id,
    build_profile_chunk_points,
    build_profile_snapshot_chunks,
)
from app.retrieval.chunks import ProfileSnapshotChunk
from app.schemas.profile_snapshot import ProfileSnapshot


def test_build_profile_chunk_point_creates_qdrant_point() -> None:
    chunk = _build_project_chunk()

    point = build_profile_chunk_point(chunk, [0.1, 0.2, 0.3])

    assert uuid.UUID(str(point.id))
    assert point.id == build_profile_chunk_point_id(chunk.chunk_id)
    assert point.vector == [0.1, 0.2, 0.3]
    assert point.payload == {
        "diagnosisId": 1,
        "chunkId": "diagnosis-1-project-3-0",
        "sourceType": "project",
        "sourceId": 3,
        "chunkIndex": 0,
        "title": "CareerChat",
        "text": "프로젝트명: CareerChat. 설명: React 프로젝트.",
        "metadata": {"snapshotVersion": 1},
    }


def test_build_profile_chunk_point_id_is_deterministic() -> None:
    chunk_id = "diagnosis-1-project-3-0"

    assert build_profile_chunk_point_id(chunk_id) == build_profile_chunk_point_id(
        chunk_id
    )


def test_build_profile_chunk_points_rejects_length_mismatch() -> None:
    chunk = _build_project_chunk()

    with pytest.raises(ValueError, match="same length"):
        build_profile_chunk_points([chunk], [])


def test_build_profile_chunk_point_rejects_empty_vector() -> None:
    chunk = _build_project_chunk()

    with pytest.raises(ValueError, match="vector must not be empty"):
        build_profile_chunk_point(chunk, [])


def test_build_profile_chunk_point_id_rejects_blank_chunk_id() -> None:
    with pytest.raises(ValueError, match="chunk_id must not be blank"):
        build_profile_chunk_point_id(" ")


def _build_project_chunk() -> ProfileSnapshotChunk:
    snapshot = ProfileSnapshot.model_validate(
        {
            "snapshotVersion": 1,
            "profile": {
                "profileId": 10,
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
    )

    return build_profile_snapshot_chunks(diagnosis_id=1, snapshot=snapshot)[0]
