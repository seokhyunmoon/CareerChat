from __future__ import annotations

from typing import Any, Protocol

from app.core.pipeline_steps import ORDERED_PIPELINE_STEPS, PipelineStep
from app.pipeline.context import AnalysisPipelineContext, AnalysisPipelineResult
from app.pipeline.reporting import AnalysisReportGenerator
from app.schemas.metadata import AnalysisMetadata, AnalysisStepMetadata


class ProfileSnapshotIndexer(Protocol):
    def index_profile_snapshot(
        self,
        *,
        diagnosis_id: int,
        payload: dict[str, Any],
    ) -> object: ...


class AnalysisPipeline:
    def __init__(
        self,
        steps: tuple[PipelineStep, ...] = ORDERED_PIPELINE_STEPS,
        profile_indexer: ProfileSnapshotIndexer | None = None,
        profile_indexing_fallback_enabled: bool = True,
        report_generator: AnalysisReportGenerator | None = None,
    ) -> None:
        self.steps = steps
        self._profile_indexer = profile_indexer
        self._profile_indexing_fallback_enabled = profile_indexing_fallback_enabled
        self._report_generator = report_generator or AnalysisReportGenerator()

    def run(self, context: AnalysisPipelineContext) -> AnalysisPipelineResult:
        self._index_profile_snapshot(context)
        report_package = self._report_generator.generate_report(context)

        return AnalysisPipelineResult(
            diagnosisId=context.diagnosisId,
            taskId=context.taskId,
            metadata=context.metadata,
            reportPackage=report_package,
        )

    def _index_profile_snapshot(self, context: AnalysisPipelineContext) -> None:
        if self._profile_indexer is None:
            _record_step_metadata(
                context.metadata,
                step=PipelineStep.PROFILE_INDEXING,
                provider_name="snapshot",
                fallback_used=True,
            )
            return

        try:
            self._profile_indexer.index_profile_snapshot(
                diagnosis_id=context.diagnosisId,
                payload=context.profileSnapshot.model_dump(mode="json"),
            )
        except Exception:
            _record_step_metadata(
                context.metadata,
                step=PipelineStep.PROFILE_INDEXING,
                provider_name="qdrant",
                fallback_used=True,
            )
            if self._profile_indexing_fallback_enabled:
                return
            raise

        _record_step_metadata(
            context.metadata,
            step=PipelineStep.PROFILE_INDEXING,
            provider_name="qdrant",
            fallback_used=False,
        )


def _record_step_metadata(
    metadata: AnalysisMetadata,
    *,
    step: PipelineStep,
    provider_name: str,
    fallback_used: bool,
) -> None:
    metadata.steps[step.value] = AnalysisStepMetadata(
        step=step.value,
        providerName=provider_name,
        fallbackUsed=fallback_used,
    )
