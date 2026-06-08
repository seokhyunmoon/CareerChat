from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.core.config import Settings
from app.core.pipeline_steps import PipelineStep
from app.pipeline.context import AnalysisPipelineContext
from app.pipeline.factory import build_default_analysis_pipeline
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.metadata import AnalysisMetadata
from app.schemas.profile_snapshot import ProfileSnapshot


def test_build_default_analysis_pipeline_indexes_snapshot_and_uses_qdrant_evidence() -> None:
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    pipeline = build_default_analysis_pipeline(
        settings=Settings(profile_retrieval_provider="qdrant"),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    result = pipeline.run(build_context())

    assert vector_store.ensure_collection_called is True
    assert vector_store.upserted_payloads is not None
    assert any(
        payload["sourceType"] == "project"
        and "Spring Boot REST API" in payload["text"]
        for payload in vector_store.upserted_payloads
    )
    assert vector_store.search_kwargs == {
        "diagnosis_id": 1,
        "query_vector": [0.1, 0.2, 0.3],
        "limit": 3,
    }
    assert embedding_provider.texts[-1].startswith("Spring Boot REST API 개발 경험")
    assert "spring boot" in embedding_provider.texts[-1]
    assert "rest api" in embedding_provider.texts[-1]

    top_job = result.reportPackage.jobs[0]
    assert top_job.requirementMatches[0].status == "matched"
    assert top_job.requirementMatches[0].evidence[0].evidence.sourceType == "project"
    assert top_job.requirementMatches[0].evidence[0].rationale == (
        "Qdrant profile evidence matched the requirement query."
    )

    metadata = result.metadata.steps
    assert metadata[PipelineStep.PROFILE_INDEXING.value].providerName == "qdrant"
    assert metadata[PipelineStep.PROFILE_INDEXING.value].fallbackUsed is False
    assert metadata[PipelineStep.EVIDENCE_RETRIEVAL.value].providerName == "qdrant"
    assert metadata[PipelineStep.EVIDENCE_RETRIEVAL.value].fallbackUsed is False


def test_build_default_analysis_pipeline_can_use_snapshot_retrieval_provider() -> None:
    pipeline = build_default_analysis_pipeline(
        settings=Settings(profile_retrieval_provider="snapshot"),
    )

    result = pipeline.run(build_context())

    metadata = result.metadata.steps
    assert metadata[PipelineStep.PROFILE_INDEXING.value].providerName == "snapshot"
    assert metadata[PipelineStep.PROFILE_INDEXING.value].fallbackUsed is True
    assert metadata[PipelineStep.EVIDENCE_RETRIEVAL.value].providerName == "snapshot"
    assert result.reportPackage.jobs[0].requirementMatches[0].evidence


def build_context() -> AnalysisPipelineContext:
    return AnalysisPipelineContext(
        diagnosisId=1,
        taskId="task-1",
        profileSnapshot=ProfileSnapshot.model_validate(
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
                        "description": "Spring Boot REST API와 Redis 작업 큐를 구현했습니다.",
                    }
                ],
                "achievements": [],
            }
        ),
        jobs=[
            AnalysisJobPosting(
                jdId=10,
                displayOrder=1,
                companyName="Backend Corp",
                position="Backend Developer",
                content="Spring Boot REST API 개발 경험",
            )
        ],
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
            retrievalTopK=3,
        ),
    )


@dataclass
class FakeEmbeddingProvider:
    texts: list[str] | None = None

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if self.texts is None:
            self.texts = []
        self.texts.extend(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]


@dataclass
class FakeVectorStore:
    ensure_collection_called: bool = False
    upserted_payloads: list[dict] | None = None
    search_kwargs: dict | None = None

    def ensure_collection(self) -> None:
        self.ensure_collection_called = True

    def upsert_profile_chunks(self, points: Sequence[object]) -> None:
        self.upserted_payloads = [dict(point.payload) for point in points]

    def search_profile_chunks(
        self,
        *,
        diagnosis_id: int,
        query_vector: list[float],
        limit: int,
    ) -> list[FakeScoredPoint]:
        self.search_kwargs = {
            "diagnosis_id": diagnosis_id,
            "query_vector": query_vector,
            "limit": limit,
        }
        payload = next(
            payload
            for payload in self.upserted_payloads or []
            if payload["sourceType"] == "project"
        )
        return [FakeScoredPoint(score=0.91, payload=payload)]


@dataclass
class FakeScoredPoint:
    score: float
    payload: dict
