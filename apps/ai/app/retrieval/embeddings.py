from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class TextEmbeddingProvider(Protocol):
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]: ...
