from __future__ import annotations

import pytest

from app.retrieval import build_diagnosis_filter


def test_build_diagnosis_filter_creates_required_qdrant_filter() -> None:
    query_filter = build_diagnosis_filter(1)

    assert query_filter.must is not None
    assert len(query_filter.must) == 1

    condition = query_filter.must[0]
    assert condition.key == "diagnosisId"
    assert condition.match is not None
    assert condition.match.value == 1


@pytest.mark.parametrize("diagnosis_id", [0, -1])
def test_build_diagnosis_filter_rejects_invalid_diagnosis_id(
    diagnosis_id: int,
) -> None:
    with pytest.raises(ValueError, match="diagnosis_id must be greater than 0"):
        build_diagnosis_filter(diagnosis_id)
