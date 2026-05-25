"""Prompt manifest and prompt template builders."""

from app.prompts.manifest import (
    DEFAULT_MODEL_NAME,
    DEFAULT_PIPELINE_VERSION,
    DEFAULT_PROMPT_SET_VERSION,
    JOB_STRUCTURING_PROMPT,
    PROMPT_SETS,
    REPORT_GENERATION_PROMPT,
    REQUIREMENT_MATCHING_PROMPT,
    PromptDefinition,
    PromptSet,
    resolve_prompt_set,
)
from app.prompts.templates import (
    build_job_structuring_prompt,
    build_report_generation_prompt,
    build_requirement_matching_prompt,
)

__all__ = [
    "DEFAULT_MODEL_NAME",
    "DEFAULT_PIPELINE_VERSION",
    "DEFAULT_PROMPT_SET_VERSION",
    "JOB_STRUCTURING_PROMPT",
    "PROMPT_SETS",
    "PromptDefinition",
    "PromptSet",
    "REPORT_GENERATION_PROMPT",
    "REQUIREMENT_MATCHING_PROMPT",
    "build_job_structuring_prompt",
    "build_report_generation_prompt",
    "build_requirement_matching_prompt",
    "resolve_prompt_set",
]
