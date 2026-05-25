from __future__ import annotations


class LLMExecutionError(RuntimeError):
    """Base exception for prompt execution failures."""


class LLMProviderError(LLMExecutionError):
    """Raised when an upstream LLM provider returns an error."""


class LLMTimeoutError(LLMExecutionError):
    """Raised when an upstream LLM provider times out."""


class InvalidLLMResponseError(LLMExecutionError):
    """Raised when an LLM response cannot be parsed into the expected schema."""
