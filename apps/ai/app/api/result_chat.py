from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.chat.service import (
    CHAT_RESPONSE_ERROR_CODE,
    ResultChatResponseGenerationError,
    get_result_chat_response_generator,
)
from app.schemas.result_chat import ResultChatResponse, ResultChatResponseRequest

router = APIRouter(prefix="/chat/responses", tags=["result-chat"])


@router.post("", response_model=ResultChatResponse)
def create_result_chat_response(
    request: ResultChatResponseRequest,
) -> ResultChatResponse:
    try:
        return get_result_chat_response_generator().generate_response(request)
    except ResultChatResponseGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": CHAT_RESPONSE_ERROR_CODE,
                "message": "Unable to generate chat response.",
            },
        ) from exc
