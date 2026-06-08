from __future__ import annotations

import pytest

from app.chat.service import (
    ResultChatResponseGenerationError,
    ResultChatResponseGenerator,
)
from app.llm.errors import LLMProviderError
from app.llm.provider import PromptExecutionRequest, PromptExecutionResult
from app.prompts import RESULT_CHAT_RESPONSE_PROMPT_VERSION
from app.schemas.result_chat import ResultChatResponseRequest
from tests.schemas.test_result_chat_schema import build_result_chat_request_body


class FakeResultChatProvider:
    provider_name = "fake"

    def __init__(self, content: str) -> None:
        self.content = content
        self.requests: list[PromptExecutionRequest] = []

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult:
        self.requests.append(request)
        return PromptExecutionResult(
            providerName=self.provider_name,
            modelName=request.modelName,
            promptKey=request.promptKey,
            promptVersion=request.promptVersion,
            content=self.content,
            durationMs=12,
        )


class FailingResultChatProvider:
    provider_name = "fake"

    def execute_prompt(
        self,
        request: PromptExecutionRequest,
    ) -> PromptExecutionResult:
        raise LLMProviderError("upstream secret error")


def test_result_chat_response_generator_returns_structured_response() -> None:
    provider = FakeResultChatProvider(
        """
        {
          "content": "현재 결과 기준으로는 토스 AI Engineer 공고를 먼저 지원하는 것이 좋습니다.",
          "referencedJobIds": [10],
          "reasonCodes": ["TOP_RANKED_JOB", "FIT_SCORE"],
          "usedFields": ["reportSummary", "jobResults.fitScore"]
        }
        """
    )
    generator = ResultChatResponseGenerator(
        llm_provider=provider,
        model_name="fake-model",
        temperature=0,
    )

    response = generator.generate_response(
        ResultChatResponseRequest.model_validate(build_result_chat_request_body())
    )

    assert response.content.startswith("현재 결과 기준")
    assert response.evidenceData.referencedJobIds == [10]
    assert response.evidenceData.reasonCodes == ["TOP_RANKED_JOB", "FIT_SCORE"]
    assert response.providerName == "fake"
    assert response.modelName == "fake-model"
    assert response.promptVersion == RESULT_CHAT_RESPONSE_PROMPT_VERSION

    prompt_request = provider.requests[0]
    assert prompt_request.responseSchemaName == "ResultChatResponseOutput"
    assert '"userMessage": "어느 공고를 먼저 지원하는 게 좋아?"' in prompt_request.userPrompt
    assert '"reportSummary": "토스 공고가 가장 적합합니다."' in prompt_request.userPrompt
    assert '"companyName": "토스"' in prompt_request.userPrompt
    assert '"previousMessages"' in prompt_request.userPrompt


def test_result_chat_response_generator_requires_configured_provider() -> None:
    generator = ResultChatResponseGenerator(
        llm_provider=None,
        model_name="fake-model",
        temperature=0,
    )

    with pytest.raises(ResultChatResponseGenerationError, match="not configured"):
        generator.generate_response(
            ResultChatResponseRequest.model_validate(build_result_chat_request_body())
        )


def test_result_chat_response_generator_hides_provider_error_details() -> None:
    generator = ResultChatResponseGenerator(
        llm_provider=FailingResultChatProvider(),
        model_name="fake-model",
        temperature=0,
    )

    with pytest.raises(ResultChatResponseGenerationError) as exc_info:
        generator.generate_response(
            ResultChatResponseRequest.model_validate(build_result_chat_request_body())
        )

    assert "upstream secret error" not in str(exc_info.value)
