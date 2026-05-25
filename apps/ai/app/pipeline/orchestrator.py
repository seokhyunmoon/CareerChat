from __future__ import annotations

from app.core.pipeline_steps import ORDERED_PIPELINE_STEPS, PipelineStep
from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.reporting import AnalysisReportGenerator


class AnalysisPipeline:
    def __init__(
        self,
        steps: tuple[PipelineStep, ...] = ORDERED_PIPELINE_STEPS,
        report_generator: AnalysisReportGenerator | None = None,
    ) -> None:
        self.steps = steps
        self._report_generator = report_generator or AnalysisReportGenerator()

    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult:
        report_package = self._report_generator.generate_report(context)

        return AnalysisPipelineResult(
            diagnosisId=context.diagnosisId,
            taskId=context.taskId,
            metadata=context.metadata,
            reportPackage=report_package,
        )
