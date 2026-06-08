from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.llm.errors import LLMExecutionError
from app.llm.factory import build_groq_llm_provider
from app.llm.provider import LLMProvider
from app.llm.structured import ResultChatResponseOutput, parse_structured_output
from app.prompts.templates import build_result_chat_response_prompt
from app.schemas.result_chat import (
    ResultChatEvidenceData,
    ResultChatResponse,
    ResultChatResponseRequest,
)

CHAT_RESPONSE_ERROR_CODE = "CHAT_RESPONSE_GENERATION_FAILED"


class ResultChatResponseGenerationError(RuntimeError):
    """Raised when a result-based chat response cannot be generated safely."""


class ResultChatResponseGenerator:
    def __init__(
        self,
        *,
        llm_provider: LLMProvider | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
        settings: Settings | None = None,
    ) -> None:
        resolved_settings = settings or get_settings()
        self._llm_provider = (
            llm_provider
            if llm_provider is not None
            else (
                build_groq_llm_provider(resolved_settings)
                if resolved_settings.llm_provider == "groq"
                else None
            )
        )
        self._model_name = model_name or resolved_settings.groq_model
        self._temperature = (
            temperature
            if temperature is not None
            else resolved_settings.groq_temperature
        )

    def generate_response(
        self,
        request: ResultChatResponseRequest,
    ) -> ResultChatResponse:
        if self._llm_provider is None:
            raise ResultChatResponseGenerationError(
                "Result chat LLM provider is not configured."
            )

        prompt_request = build_result_chat_response_prompt(
            request=request,
            model_name=self._model_name,
            temperature=self._temperature,
        )

        try:
            execution = self._llm_provider.execute_prompt(prompt_request)
            output = parse_structured_output(
                content=execution.content,
                schema=ResultChatResponseOutput,
            )
        except LLMExecutionError as exc:
            raise ResultChatResponseGenerationError(
                "Failed to generate result chat response."
            ) from exc

        return ResultChatResponse(
            content=output.content,
            evidenceData=ResultChatEvidenceData(
                referencedJobIds=output.referencedJobIds,
                reasonCodes=output.reasonCodes,
                usedFields=output.usedFields,
            ),
            providerName=execution.providerName,
            modelName=execution.modelName,
            promptKey=execution.promptKey,
            promptVersion=execution.promptVersion,
        )


@lru_cache
def get_result_chat_response_generator() -> ResultChatResponseGenerator:
    return ResultChatResponseGenerator()
