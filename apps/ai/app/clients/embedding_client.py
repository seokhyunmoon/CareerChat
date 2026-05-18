from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings


def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()

    return HuggingFaceEmbeddings(model_name=settings.embedding_model)
