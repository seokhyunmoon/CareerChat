from __future__ import annotations

from time import perf_counter
from typing import Any

from pydantic import SecretStr

from app.llm.errors import LLMProviderError, LLMTimeoutError
from app.llm.provider import PromptExecutionRequest, PromptExecutionResult


class GroqLLMProvider:
    provider_name = "groq"

    def __init__(
        self,
        *,
        api_key: str,
        timeout_seconds: float,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0")

        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult:
        started_at = perf_counter()

        try:
            message = self._build_client(request).invoke(
                [
                    _build_system_message(request.systemPrompt),
                    _build_human_message(request.userPrompt),
                ]
            )
        except TimeoutError as exc:
            raise LLMTimeoutError("Groq LLM request timed out") from exc
        except Exception as exc:
            if _is_timeout_exception(exc):
                raise LLMTimeoutError("Groq LLM request timed out") from exc
            raise LLMProviderError(f"Groq LLM request failed: {exc}") from exc

        return PromptExecutionResult(
            providerName=self.provider_name,
            modelName=request.modelName,
            promptKey=request.promptKey,
            promptVersion=request.promptVersion,
            content=_extract_message_content(message),
            durationMs=round((perf_counter() - started_at) * 1000),
            retryCount=self._max_retries,
        )

    def _build_client(self, request: PromptExecutionRequest) -> Any:
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=request.modelName,
            temperature=request.temperature if request.temperature is not None else 0.0,
            api_key=SecretStr(self._api_key),
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
        )


def _build_system_message(content: str) -> Any:
    from langchain_core.messages import SystemMessage

    return SystemMessage(content=content)


def _build_human_message(content: str) -> Any:
    from langchain_core.messages import HumanMessage

    return HumanMessage(content=content)


def _extract_message_content(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(_extract_content_part(part) for part in content).strip()

    return str(content)


def _extract_content_part(part: Any) -> str:
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        value = part.get("text") or part.get("content") or ""
        return str(value)
    return str(part)


def _is_timeout_exception(exc: Exception) -> bool:
    return "timeout" in exc.__class__.__name__.lower()
