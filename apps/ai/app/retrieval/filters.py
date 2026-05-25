from __future__ import annotations

from qdrant_client import models


def build_diagnosis_filter(diagnosis_id: int) -> models.Filter:
    if diagnosis_id < 1:
        raise ValueError("diagnosis_id must be greater than 0")

    return models.Filter(
        must=[
            models.FieldCondition(
                key="diagnosisId",
                match=models.MatchValue(value=diagnosis_id),
            )
        ]
    )
