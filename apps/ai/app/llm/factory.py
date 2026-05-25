from __future__ import annotations

from app.core.config import Settings, get_settings
from app.llm.groq import GroqLLMProvider
from app.llm.provider import LLMProvider


def build_groq_llm_provider(settings: Settings | None = None) -> LLMProvider | None:
    resolved_settings = settings or get_settings()
    if not resolved_settings.groq_api_key:
        return None

    return GroqLLMProvider(
        api_key=resolved_settings.groq_api_key,
        timeout_seconds=resolved_settings.groq_timeout_seconds,
        max_retries=resolved_settings.groq_max_retries,
    )
