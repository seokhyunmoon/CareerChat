from __future__ import annotations

from qdrant_client import QdrantClient

from app.core.config import Settings, get_settings
from app.retrieval.embeddings import TextEmbeddingProvider
from app.retrieval.indexing import (
    ProfileSnapshotIndexingService,
    ProfileVectorStoreWriter,
)
from app.retrieval.sentence_transformers import SentenceTransformersEmbeddingProvider
from app.retrieval.vector_store import ProfileVectorStore, QdrantProfileClient


def build_profile_vector_store(
    *,
    settings: Settings | None = None,
    client: QdrantProfileClient | None = None,
) -> ProfileVectorStore:
    resolved_settings = settings or get_settings()
    resolved_client = client or QdrantClient(
        url=resolved_settings.qdrant_url,
        api_key=resolved_settings.qdrant_api_key,
    )

    return ProfileVectorStore(
        client=resolved_client,
        collection_name=resolved_settings.qdrant_collection_name,
        vector_size=resolved_settings.qdrant_vector_size,
    )


def build_profile_snapshot_indexing_service(
    *,
    embedding_provider: TextEmbeddingProvider,
    settings: Settings | None = None,
    vector_store: ProfileVectorStoreWriter | None = None,
) -> ProfileSnapshotIndexingService:
    resolved_vector_store = vector_store or build_profile_vector_store(
        settings=settings
    )

    return ProfileSnapshotIndexingService(
        embedding_provider=embedding_provider,
        vector_store=resolved_vector_store,
    )


def build_default_profile_snapshot_indexing_service(
    *,
    settings: Settings | None = None,
    vector_store: ProfileVectorStoreWriter | None = None,
) -> ProfileSnapshotIndexingService:
    resolved_settings = settings or get_settings()
    return build_profile_snapshot_indexing_service(
        embedding_provider=SentenceTransformersEmbeddingProvider(
            model_name=resolved_settings.embedding_model,
        ),
        settings=resolved_settings,
        vector_store=vector_store,
    )
