from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

import app.api.analysis_jobs as analysis_jobs_api
from app.main import app
from app.prompts.manifest import (
    DEFAULT_MODEL_NAME,
    DEFAULT_PIPELINE_VERSION,
    DEFAULT_PROMPT_SET_VERSION,
)
from app.workers.payloads import AnalysisTaskPayload


client = TestClient(app)


def build_analysis_job_request_body() -> dict:
    return {
        "diagnosisId": 1,
        "callback": {
            "completeUrl": "http://localhost:8080/api/internal/ai/callback/complete",
            "failUrl": "http://localhost:8080/api/internal/ai/callback/fail",
        },
        "profileSnapshot": {
            "snapshotVersion": 1,
            "profile": {
                "profileId": 1,
                "experienceLevel": "JUNIOR",
            },
            "education": [],
            "workExperiences": [],
            "projects": [],
            "achievements": [],
        },
        "jobs": [
            {
                "jdId": 1,
                "displayOrder": 1,
                "companyName": "CareerChat",
                "position": "Backend Developer",
                "content": "Python and Spring experience required.",
            },
        ],
    }


def test_create_analysis_job_returns_queued_task_and_enqueues_payload(monkeypatch) -> None:
    enqueued_payloads: list[AnalysisTaskPayload] = []

    def fake_enqueue_analysis_task(payload: AnalysisTaskPayload) -> None:
        enqueued_payloads.append(payload)

    monkeypatch.setattr(analysis_jobs_api, "enqueue_analysis_task", fake_enqueue_analysis_task)

    response = client.post(
        "/analysis/jobs",
        json=build_analysis_job_request_body(),
    )

    assert response.status_code == 202
    body = response.json()
    assert body["diagnosisId"] == 1
    assert body["status"] == "QUEUED"
    assert UUID(body["taskId"])

    assert len(enqueued_payloads) == 1
    payload = enqueued_payloads[0]
    assert payload.diagnosisId == body["diagnosisId"]
    assert payload.taskId == body["taskId"]
    assert payload.callback.completeUrl.unicode_string().endswith("/complete")
    assert payload.callback.failUrl.unicode_string().endswith("/fail")
    assert payload.metadata.pipelineVersion == DEFAULT_PIPELINE_VERSION
    assert payload.metadata.promptSetVersion == DEFAULT_PROMPT_SET_VERSION
    assert payload.metadata.defaultModel == DEFAULT_MODEL_NAME
