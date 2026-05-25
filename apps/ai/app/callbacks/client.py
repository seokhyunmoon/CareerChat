from __future__ import annotations

import httpx

from app.core.config import Settings, get_settings
from app.schemas.analysis_job import CallbackTarget
from app.schemas.callback import CompleteCallbackPayload, FailCallbackPayload


class SpringCallbackClient:
    def __init__(
        self,
        *,
        internal_token: str | None,
        timeout_seconds: float,
        client: httpx.Client | None = None,
    ) -> None:
        self.internal_token = internal_token
        self.timeout_seconds = timeout_seconds
        self.client = client or httpx.Client(timeout=timeout_seconds)

    def post_complete(
        self,
        *,
        callback: CallbackTarget,
        payload: CompleteCallbackPayload,
    ) -> httpx.Response:
        response = self.client.post(
            callback.completeUrl.unicode_string(),
            json=payload.model_dump(mode="json"),
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response

    def post_fail(
        self,
        *,
        callback: CallbackTarget,
        payload: FailCallbackPayload,
    ) -> httpx.Response:
        response = self.client.post(
            callback.failUrl.unicode_string(),
            json=payload.model_dump(mode="json"),
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response

    def _headers(self) -> dict[str, str]:
        if self.internal_token is None or self.internal_token.strip() == "":
            return {}

        return {"Authorization": f"Bearer {self.internal_token}"}


def build_spring_callback_client(
    *,
    settings: Settings | None = None,
    client: httpx.Client | None = None,
) -> SpringCallbackClient:
    resolved_settings = settings or get_settings()
    return SpringCallbackClient(
        internal_token=resolved_settings.spring_callback_internal_token,
        timeout_seconds=resolved_settings.callback_timeout_seconds,
        client=client,
    )
