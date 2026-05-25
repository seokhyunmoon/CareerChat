from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from sentence_transformers import SentenceTransformer


class SentenceTransformerModel(Protocol):
    def encode(
        self,
        sentences: Sequence[str],
        *,
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
    ) -> object: ...


class SentenceTransformersEmbeddingProvider:
    def __init__(
        self,
        *,
        model_name: str,
        model: SentenceTransformerModel | None = None,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name must not be blank")

        self._model_name = model_name
        self._model = model

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        normalized_texts = _normalize_texts(texts)
        if not normalized_texts:
            return []

        embeddings = self._get_model().encode(
            normalized_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return [[float(value) for value in embedding] for embedding in embeddings]

    def _get_model(self) -> SentenceTransformerModel:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model


def _normalize_texts(texts: Sequence[str]) -> list[str]:
    return [" ".join(text.split()) for text in texts if text and text.strip()]
