from __future__ import annotations

from fastapi.testclient import TestClient

import app.api.result_chat as result_chat_api
from app.main import app
from app.schemas.result_chat import (
    ResultChatEvidenceData,
    ResultChatResponse,
    ResultChatResponseRequest,
)
from tests.schemas.test_result_chat_schema import build_result_chat_request_body

client = TestClient(app)


class FakeResultChatResponseGenerator:
    def generate_response(
        self,
        request: ResultChatResponseRequest,
    ) -> ResultChatResponse:
        return ResultChatResponse(
            content=f"{request.jobResults[0].companyName} 공고를 먼저 검토하세요.",
            evidenceData=ResultChatEvidenceData(
                referencedJobIds=[request.jobResults[0].jdId],
                reasonCodes=["TOP_RANKED_JOB"],
                usedFields=["jobResults.rankOrder"],
            ),
            providerName="fake",
            modelName="fake-model",
            promptKey="result_chat_response",
            promptVersion="result-chat-response-v1",
        )


class FailingResultChatResponseGenerator:
    def generate_response(
        self,
        request: ResultChatResponseRequest,
    ) -> ResultChatResponse:
        raise result_chat_api.ResultChatResponseGenerationError("internal provider detail")


def test_create_result_chat_response_returns_assistant_response(monkeypatch) -> None:
    monkeypatch.setattr(
        result_chat_api,
        "get_result_chat_response_generator",
        lambda: FakeResultChatResponseGenerator(),
    )

    response = client.post(
        "/chat/responses",
        json=build_result_chat_request_body(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "토스 공고를 먼저 검토하세요."
    assert body["evidenceData"]["referencedJobIds"] == [10]
    assert body["providerName"] == "fake"
    assert body["promptVersion"] == "result-chat-response-v1"


def test_create_result_chat_response_hides_internal_error(monkeypatch) -> None:
    monkeypatch.setattr(
        result_chat_api,
        "get_result_chat_response_generator",
        lambda: FailingResultChatResponseGenerator(),
    )

    response = client.post(
        "/chat/responses",
        json=build_result_chat_request_body(),
    )

    assert response.status_code == 503
    body = response.json()
    assert body["detail"]["code"] == "CHAT_RESPONSE_GENERATION_FAILED"
    assert body["detail"]["message"] == "Unable to generate chat response."
    assert "internal provider detail" not in str(body)
