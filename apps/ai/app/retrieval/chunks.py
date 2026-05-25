from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.profile_snapshot import ProfileEvidenceReference

ProfileChunkSourceType = Literal[
    "education",
    "work_experience",
    "project",
    "achievement",
    "profile_overview",
]


class QdrantProfileChunkPayload(BaseModel):
    diagnosisId: int = Field(ge=1)
    chunkId: str = Field(min_length=1)
    sourceType: ProfileChunkSourceType
    sourceId: int | str | None = None
    chunkIndex: int = Field(ge=0)
    title: str | None = None
    text: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProfileSnapshotChunk(BaseModel):
    diagnosis_id: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    evidence: ProfileEvidenceReference
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_qdrant_payload(self) -> QdrantProfileChunkPayload:
        return QdrantProfileChunkPayload(
            diagnosisId=self.diagnosis_id,
            chunkId=self.chunk_id,
            sourceType=self.evidence.sourceType,
            sourceId=self.evidence.sourceId,
            chunkIndex=self.evidence.chunkIndex,
            title=self.evidence.title,
            text=self.evidence.text or self.text,
            metadata=self.metadata,
        )
