from __future__ import annotations

import os

from langchain_groq import ChatGroq

from app.core.config import get_settings


def get_llm() -> ChatGroq:
    settings = get_settings()

    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Create apps/ai/.env from .env.example first."
        )

    os.environ.setdefault("GROQ_API_KEY", settings.groq_api_key)

    return ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
    )
