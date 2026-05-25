from __future__ import annotations

from dataclasses import dataclass

from app.core.pipeline_steps import PipelineStep


DEFAULT_MODEL_NAME = "llama-3.3-70b-versatile"
DEFAULT_PIPELINE_VERSION = "ai-diagnosis-v1"
DEFAULT_PROMPT_SET_VERSION = "diagnosis-prompt-set-v1"


@dataclass(frozen=True)
class PromptDefinition:
    key: str
    version: str
    step: PipelineStep
    template_path: str
    default_model: str = DEFAULT_MODEL_NAME


@dataclass(frozen=True)
class PromptSet:
    version: str
    pipeline_version: str
    prompts: dict[str, PromptDefinition]


JOB_STRUCTURING_PROMPT = PromptDefinition(
    key="job_structuring",
    version="job-structuring-v1",
    step=PipelineStep.JOB_STRUCTURING,
    template_path="job_structuring_v1.md",
)

REQUIREMENT_MATCHING_PROMPT = PromptDefinition(
    key="requirement_matching",
    version="requirement-matching-v1",
    step=PipelineStep.REQUIREMENT_MATCHING,
    template_path="requirement_matching_v1.md",
)

REPORT_GENERATION_PROMPT = PromptDefinition(
    key="report_generation",
    version="report-generation-v1",
    step=PipelineStep.REPORT_GENERATION,
    template_path="report_generation_v1.md",
)

PROMPT_SETS: dict[str, PromptSet] = {
    DEFAULT_PROMPT_SET_VERSION: PromptSet(
        version=DEFAULT_PROMPT_SET_VERSION,
        pipeline_version=DEFAULT_PIPELINE_VERSION,
        prompts={
            JOB_STRUCTURING_PROMPT.key: JOB_STRUCTURING_PROMPT,
            REQUIREMENT_MATCHING_PROMPT.key: REQUIREMENT_MATCHING_PROMPT,
            REPORT_GENERATION_PROMPT.key: REPORT_GENERATION_PROMPT,
        },
    ),
}


def resolve_prompt_set(version: str = DEFAULT_PROMPT_SET_VERSION) -> PromptSet:
    try:
        return PROMPT_SETS[version]
    except KeyError as exc:
        raise ValueError(f"Unknown prompt set version: {version}") from exc
