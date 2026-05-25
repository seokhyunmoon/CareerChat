from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_can_be_overridden_by_field_name() -> None:
    settings = Settings(
        qdrant_url="http://qdrant:6333",
        qdrant_collection_name="test_profile_chunks",
        qdrant_vector_size=768,
    )

    assert settings.qdrant_url == "http://qdrant:6333"
    assert settings.qdrant_collection_name == "test_profile_chunks"
    assert settings.qdrant_vector_size == 768


def test_settings_reject_invalid_qdrant_vector_size() -> None:
    with pytest.raises(ValidationError):
        Settings(qdrant_vector_size=0)
