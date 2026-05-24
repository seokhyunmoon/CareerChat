from __future__ import annotations

from app.core.pipeline_steps import ORDERED_PIPELINE_STEPS, PipelineStep
from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult


class AnalysisPipeline:
    def __init__(
        self,
        steps: tuple[PipelineStep, ...] = ORDERED_PIPELINE_STEPS,
    ) -> None:
        self.steps = steps

    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult:
        raise NotImplementedError(
            "AnalysisPipeline.run will be implemented with Qdrant, LLM, "
            "report packaging, and Spring callback execution in follow-up issues."
        )
