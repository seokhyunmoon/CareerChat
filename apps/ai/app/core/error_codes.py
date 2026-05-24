from __future__ import annotations

from enum import Enum


class AnalysisErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    PROFILE_SNAPSHOT_INVALID = "PROFILE_SNAPSHOT_INVALID"
    JOB_POSTING_INVALID = "JOB_POSTING_INVALID"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    QDRANT_ERROR = "QDRANT_ERROR"
    AI_TIMEOUT = "AI_TIMEOUT"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    INVALID_AI_RESPONSE = "INVALID_AI_RESPONSE"
    CALLBACK_FAILED = "CALLBACK_FAILED"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


RETRYABLE_ERROR_CODES: frozenset[AnalysisErrorCode] = frozenset(
    {
        AnalysisErrorCode.EMBEDDING_ERROR,
        AnalysisErrorCode.QDRANT_ERROR,
        AnalysisErrorCode.AI_TIMEOUT,
        AnalysisErrorCode.LLM_TIMEOUT,
        AnalysisErrorCode.LLM_PROVIDER_ERROR,
        AnalysisErrorCode.CALLBACK_FAILED,
        AnalysisErrorCode.UNEXPECTED_ERROR,
    }
)


def is_retryable_error(error_code: AnalysisErrorCode | str) -> bool:
    if isinstance(error_code, str):
        try:
            error_code = AnalysisErrorCode(error_code)
        except ValueError:
            return False

    return error_code in RETRYABLE_ERROR_CODES
