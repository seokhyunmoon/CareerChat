from __future__ import annotations

import sys
from pathlib import Path

import pytest

AI_APP_ROOT = Path(__file__).resolve().parents[1]

if str(AI_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_APP_ROOT))

from app.core.config import get_settings  # noqa: E402


@pytest.fixture(autouse=True)
def default_to_deterministic_llm_provider(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("LLM_PROVIDER", "deterministic")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
