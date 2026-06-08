"""LLM provider client package for production analysis calls."""

from app.llm.errors import (
    InvalidLLMResponseError,
    LLMExecutionError,
    LLMProviderError,
    LLMTimeoutError,
)
from app.llm.factory import build_groq_llm_provider
from app.llm.groq import GroqLLMProvider
from app.llm.provider import (
    LLMProvider,
    PromptExecutionRequest,
    PromptExecutionResult,
)
from app.llm.structured import (
    JobRequirementsOutput,
    ReportGenerationOutput,
    ReportJobSummary,
    RequirementMatchDecision,
    ResultChatResponseOutput,
    parse_structured_output,
    resolve_response_schema,
)

__all__ = [
    "GroqLLMProvider",
    "InvalidLLMResponseError",
    "JobRequirementsOutput",
    "LLMExecutionError",
    "LLMProvider",
    "LLMProviderError",
    "LLMTimeoutError",
    "PromptExecutionRequest",
    "PromptExecutionResult",
    "ReportGenerationOutput",
    "ReportJobSummary",
    "RequirementMatchDecision",
    "ResultChatResponseOutput",
    "build_groq_llm_provider",
    "parse_structured_output",
    "resolve_response_schema",
]
