from __future__ import annotations

import pytest

from app.retrieval import (
    build_profile_snapshot_chunks,
    build_safe_profile_snapshot_chunks,
)
from app.schemas.profile_snapshot import ProfileSnapshot


def test_build_profile_snapshot_chunks_creates_profile_and_project_chunks() -> None:
    snapshot = ProfileSnapshot.model_validate(
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
                    "description": "React와 Spring Boot 기반 진단 서비스",
                }
            ],
            "achievements": [],
        }
    )

    chunks = build_profile_snapshot_chunks(diagnosis_id=1, snapshot=snapshot)

    assert [chunk.chunk_id for chunk in chunks] == [
        "diagnosis-1-profile_overview-10-0",
        "diagnosis-1-project-3-0",
    ]
    assert chunks[0].text == "프로필 요약. 경력 수준: junior."
    assert chunks[1].text == (
        "프로젝트명: CareerChat. 설명: React와 Spring Boot 기반 진단 서비스."
    )


def test_build_profile_snapshot_chunks_splits_long_project_with_context() -> None:
    snapshot = ProfileSnapshot.model_validate(
        {
            "snapshotVersion": 1,
            "profile": {
                "profileId": 10,
                "experienceLevel": None,
            },
            "education": [],
            "workExperiences": [],
            "projects": [
                {
                    "projectId": 3,
                    "projectName": "CareerChat",
                    "description": "React와 Spring Boot 기반 진단 서비스. " * 20,
                }
            ],
            "achievements": [],
        }
    )

    chunks = build_profile_snapshot_chunks(
        diagnosis_id=1,
        snapshot=snapshot,
        max_chunk_text_length=120,
        chunk_overlap=20,
    )

    assert len(chunks) > 1
    assert [chunk.chunk_id for chunk in chunks[:2]] == [
        "diagnosis-1-project-3-0",
        "diagnosis-1-project-3-1",
    ]
    assert all(
        chunk.text.startswith("프로젝트명: CareerChat.") for chunk in chunks
    )


def test_profile_snapshot_chunk_can_be_converted_to_qdrant_payload() -> None:
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
    chunk = build_profile_snapshot_chunks(diagnosis_id=1, snapshot=snapshot)[0]

    payload = chunk.to_qdrant_payload()

    assert payload.diagnosisId == 1
    assert payload.chunkId == "diagnosis-1-project-3-0"
    assert payload.sourceType == "project"
    assert payload.sourceId == 3
    assert payload.chunkIndex == 0
    assert payload.text == "프로젝트명: CareerChat. 설명: React 프로젝트."
    assert payload.metadata == {"snapshotVersion": 1}


def test_build_safe_profile_snapshot_chunks_accepts_valid_payload() -> None:
    chunks = build_safe_profile_snapshot_chunks(
        diagnosis_id=1,
        payload={
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
        },
    )

    assert [chunk.chunk_id for chunk in chunks] == [
        "diagnosis-1-profile_overview-10-0",
        "diagnosis-1-project-3-0",
    ]


def test_build_safe_profile_snapshot_chunks_rejects_disallowed_keys() -> None:
    payload = {
        "snapshotVersion": 1,
        "profile": {
            "profileId": 10,
        },
        "education": [],
        "workExperiences": [],
        "projects": [],
        "achievements": [],
        "unexpected": "value",
    }

    with pytest.raises(ValueError, match="disallowed keys: unexpected"):
        build_safe_profile_snapshot_chunks(diagnosis_id=1, payload=payload)


def test_build_safe_profile_snapshot_chunks_rejects_nested_pii_keys() -> None:
    payload = {
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
                "email": "user@example.com",
            }
        ],
        "achievements": [],
    }

    with pytest.raises(ValueError, match="PII keys: email"):
        build_safe_profile_snapshot_chunks(diagnosis_id=1, payload=payload)


@pytest.mark.parametrize(
    ("max_chunk_text_length", "chunk_overlap"),
    [
        (0, 0),
        (100, -1),
        (100, 100),
    ],
)
def test_build_profile_snapshot_chunks_rejects_invalid_split_config(
    max_chunk_text_length: int,
    chunk_overlap: int,
) -> None:
    snapshot = ProfileSnapshot.model_validate(
        {
            "snapshotVersion": 1,
            "profile": {
                "profileId": 10,
            },
            "education": [],
            "workExperiences": [],
            "projects": [],
            "achievements": [],
        }
    )

    with pytest.raises(ValueError):
        build_profile_snapshot_chunks(
            diagnosis_id=1,
            snapshot=snapshot,
            max_chunk_text_length=max_chunk_text_length,
            chunk_overlap=chunk_overlap,
        )
