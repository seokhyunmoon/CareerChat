from __future__ import annotations

import pytest

from app.pipeline.evidence_retrieval import SnapshotProfileEvidenceRetriever
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
