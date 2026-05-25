from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class PromptExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    promptKey: str = Field(min_length=1)
    promptVersion: str = Field(min_length=1)
    modelName: str = Field(min_length=1)
    systemPrompt: str = Field(min_length=1)
    userPrompt: str = Field(min_length=1)
    responseSchemaName: str | None = Field(default=None, min_length=1)
    temperature: float | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    providerName: str = Field(min_length=1)
    modelName: str = Field(min_length=1)
    promptKey: str = Field(min_length=1)
    promptVersion: str = Field(min_length=1)
    content: str = Field(min_length=1)
    durationMs: int | None = Field(default=None, ge=0)
    retryCount: int = Field(default=0, ge=0)


class LLMProvider(Protocol):
    @property
    def provider_name(self) -> str: ...

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult: ...
