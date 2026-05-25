from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
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
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        validation_alias="EMBEDDING_MODEL",
        min_length=1,
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
