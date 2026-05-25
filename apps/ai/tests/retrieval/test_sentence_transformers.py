from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pytest

from app.retrieval import SentenceTransformersEmbeddingProvider


def test_sentence_transformers_embedding_provider_normalizes_and_embeds_texts() -> None:
    model = FakeSentenceTransformerModel()
    provider = SentenceTransformersEmbeddingProvider(
        model_name="test-model",
        model=model,
    )

    vectors = provider.embed_texts(["  React   프로젝트  ", "", "Spring Boot"])

    assert model.sentences == ["React 프로젝트", "Spring Boot"]
    assert model.convert_to_numpy is True
    assert model.normalize_embeddings is True
    assert vectors == [[0.1, 0.2], [1.1, 1.2]]


def test_sentence_transformers_embedding_provider_returns_empty_for_empty_texts() -> None:
    model = FakeSentenceTransformerModel()
    provider = SentenceTransformersEmbeddingProvider(
        model_name="test-model",
        model=model,
    )

    assert provider.embed_texts([" ", ""]) == []
    assert model.sentences is None


def test_sentence_transformers_embedding_provider_rejects_blank_model_name() -> None:
    with pytest.raises(ValueError, match="model_name must not be blank"):
        SentenceTransformersEmbeddingProvider(model_name=" ")


@dataclass
class FakeSentenceTransformerModel:
    sentences: list[str] | None = None
    convert_to_numpy: bool | None = None
    normalize_embeddings: bool | None = None

    def encode(
        self,
        sentences: Sequence[str],
        *,
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
    ) -> list[list[float]]:
        self.sentences = list(sentences)
        self.convert_to_numpy = convert_to_numpy
        self.normalize_embeddings = normalize_embeddings
        return [
            [float(index) + 0.1, float(index) + 0.2]
            for index, _ in enumerate(sentences)
        ]
