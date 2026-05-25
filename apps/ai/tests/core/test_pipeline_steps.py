from __future__ import annotations

from app.core.pipeline_steps import ORDERED_PIPELINE_STEPS, PipelineStep, pipeline_step_values


def test_pipeline_steps_end_with_result_packaging() -> None:
    assert ORDERED_PIPELINE_STEPS[-1] == PipelineStep.RESULT_PACKAGING


def test_pipeline_steps_do_not_include_worker_callback_delivery() -> None:
    assert "SPRING_CALLBACK" not in pipeline_step_values()
