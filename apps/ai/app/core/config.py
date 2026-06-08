from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

AI_APP_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=AI_APP_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    llm_provider: Literal["deterministic", "groq"] = Field(
        default="deterministic",
        validation_alias="LLM_PROVIDER",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="GROQ_MODEL",
        min_length=1,
    )
    groq_temperature: float = Field(
        default=0.0,
        validation_alias="GROQ_TEMPERATURE",
        ge=0,
    )
    groq_timeout_seconds: float = Field(
        default=30.0,
        validation_alias="GROQ_TIMEOUT_SECONDS",
        gt=0,
    )
    groq_max_retries: int = Field(
        default=2,
        validation_alias="GROQ_MAX_RETRIES",
        ge=0,
    )
    llm_deterministic_fallback_enabled: bool = Field(
        default=True,
        validation_alias="LLM_DETERMINISTIC_FALLBACK_ENABLED",
    )
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        validation_alias="EMBEDDING_MODEL",
        min_length=1,
    )
    profile_retrieval_provider: Literal["qdrant", "snapshot"] = Field(
        default="qdrant",
        validation_alias="PROFILE_RETRIEVAL_PROVIDER",
    )
    qdrant_url: str = Field(
        default="http://localhost:6333",
        validation_alias="QDRANT_URL",
        min_length=1,
    )
    qdrant_api_key: str | None = Field(
        default=None,
        validation_alias="QDRANT_API_KEY",
    )
    qdrant_collection_name: str = Field(
        default="careerchat_profile_chunks",
        validation_alias="QDRANT_COLLECTION_NAME",
        min_length=1,
    )
    qdrant_vector_size: int = Field(
        default=384,
        validation_alias="QDRANT_VECTOR_SIZE",
        ge=1,
    )
    redis_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_BROKER_URL",
        min_length=1,
    )
    redis_result_backend_url: str = Field(
        default="redis://localhost:6379/1",
        validation_alias="REDIS_RESULT_BACKEND_URL",
        min_length=1,
    )
    spring_callback_internal_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SPRING_CALLBACK_INTERNAL_TOKEN", "AI_CALLBACK_TOKEN"),
    )
    callback_timeout_seconds: float = Field(
        default=10.0,
        validation_alias="CALLBACK_TIMEOUT_SECONDS",
        gt=0,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
