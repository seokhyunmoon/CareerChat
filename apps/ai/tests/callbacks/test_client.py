from __future__ import annotations

import httpx

from app.callbacks.client import SpringCallbackClient, build_spring_callback_client
from app.callbacks.payloads import (
    build_complete_callback_payload,
    build_fail_callback_payload,
)
from app.core.config import Settings
from app.schemas.analysis_job import CallbackTarget
from tests.callbacks.test_callback_payloads import build_pipeline_result, build_task_payload


def build_callback_target() -> CallbackTarget:
    return CallbackTarget(
        completeUrl="http://localhost:8080/internal/ai/diagnoses/1/complete",
        failUrl="http://localhost:8080/internal/ai/diagnoses/1/fail",
    )


def test_post_complete_sends_authorization_header_and_payload() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"success": True})

    task_payload = build_task_payload()
    callback_payload = build_complete_callback_payload(
        result=build_pipeline_result(task_payload),
    )
    callback_client = SpringCallbackClient(
        internal_token="callback-token",
        timeout_seconds=3,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = callback_client.post_complete(
        callback=build_callback_target(),
        payload=callback_payload,
    )

    assert response.status_code == 200
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "http://localhost:8080/internal/ai/diagnoses/1/complete"
    assert request.headers["Authorization"] == "Bearer callback-token"
    assert request.headers["Content-Type"] == "application/json"
    assert b'"taskId":"task-1"' in request.content


def test_post_fail_sends_fail_payload_to_fail_url() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"success": True})

    task_payload = build_task_payload()
    callback_payload = build_fail_callback_payload(
        task_payload=task_payload,
        exc=RuntimeError("failed"),
    )
    callback_client = SpringCallbackClient(
        internal_token="callback-token",
        timeout_seconds=3,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = callback_client.post_fail(
        callback=build_callback_target(),
        payload=callback_payload,
    )

    assert response.status_code == 200
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "http://localhost:8080/internal/ai/diagnoses/1/fail"
    assert request.headers["Authorization"] == "Bearer callback-token"
    assert b'"errorMessage":"failed"' in request.content


def test_post_complete_raises_for_non_success_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"success": False}, request=request)

    task_payload = build_task_payload()
    callback_payload = build_complete_callback_payload(
        result=build_pipeline_result(task_payload),
    )
    callback_client = SpringCallbackClient(
        internal_token=None,
        timeout_seconds=3,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    try:
        callback_client.post_complete(
            callback=build_callback_target(),
            payload=callback_payload,
        )
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 500
    else:
        raise AssertionError("Expected HTTPStatusError")


def test_build_spring_callback_client_uses_settings() -> None:
    callback_client = build_spring_callback_client(
        settings=Settings(
            spring_callback_internal_token="callback-token",
            callback_timeout_seconds=7,
        ),
        client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200))),
    )

    assert callback_client.internal_token == "callback-token"
    assert callback_client.timeout_seconds == 7
