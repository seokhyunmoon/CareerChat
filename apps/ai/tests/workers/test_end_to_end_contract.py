from __future__ import annotations

import json

from app.schemas.analysis_job import AnalysisJobRequest
from app.schemas.callback import CompleteCallbackPayload, FailCallbackPayload
from app.schemas.metadata import AnalysisMetadata
from app.workers.payloads import AnalysisTaskPayload
from app.workers.tasks import execute_analysis_task


class FakeCallbackClient:
    def __init__(self) -> None:
        self.complete_payloads: list[CompleteCallbackPayload] = []
        self.fail_payloads: list[FailCallbackPayload] = []

    def post_complete(self, *, callback, payload: CompleteCallbackPayload) -> None:
        self.complete_payloads.append(payload)

    def post_fail(self, *, callback, payload: FailCallbackPayload) -> None:
        self.fail_payloads.append(payload)


def build_analysis_job_request() -> AnalysisJobRequest:
    return AnalysisJobRequest.model_validate(
        {
            "diagnosisId": 1,
            "callback": {
                "completeUrl": "http://localhost:8080/internal/ai/diagnoses/1/complete",
                "failUrl": "http://localhost:8080/internal/ai/diagnoses/1/fail",
            },
            "profileSnapshot": {
                "snapshotVersion": 1,
                "profile": {
                    "profileId": 10,
                    "experienceLevel": "junior",
                },
                "education": [],
                "workExperiences": [],
                "projects": [
                    {
                        "projectId": 3,
                        "projectName": "CareerChat",
                        "description": (
                            "Spring Boot REST API와 Redis 기반 비동기 작업 큐를 "
                            "구현했습니다."
                        ),
                    }
                ],
                "achievements": [],
            },
            "jobs": [
                {
                    "jdId": 10,
                    "displayOrder": 1,
                    "companyName": "Backend Corp",
                    "position": "Backend Developer",
                    "content": "\n".join(
                        [
                            "- Spring Boot REST API 개발 경험",
                            "- Redis 기반 비동기 처리 경험 우대",
                        ]
                    ),
                },
                {
                    "jdId": 11,
                    "displayOrder": 2,
                    "companyName": "Infra Corp",
                    "position": "Platform Engineer",
                    "content": "\n".join(
                        [
                            "- Kubernetes 운영 경험",
                            "- Terraform 기반 인프라 자동화 경험",
                        ]
                    ),
                },
            ],
        }
    )


def build_task_payload() -> AnalysisTaskPayload:
    return AnalysisTaskPayload.from_request(
        request=build_analysis_job_request(),
        task_id="task-1",
        metadata=AnalysisMetadata(
            pipelineVersion="ai-diagnosis-v1",
            promptSetVersion="diagnosis-prompt-set-v1",
            defaultModel="llama-3.3-70b-versatile",
            retrievalTopK=3,
        ),
    )


def test_worker_pipeline_complete_callback_contract_end_to_end() -> None:
    task_payload = build_task_payload()
    callback_client = FakeCallbackClient()

    result = execute_analysis_task(
        task_payload,
        callback_client=callback_client,
    )

    assert callback_client.fail_payloads == []
    assert len(callback_client.complete_payloads) == 1

    complete_payload = callback_client.complete_payloads[0]
    assert complete_payload.taskId == "task-1"
    assert complete_payload.reportSummary == result.reportPackage.reportSummary
    assert complete_payload.reportContent == result.reportPackage.reportContent
    assert complete_payload.modelName == "llama-3.3-70b-versatile"
    assert complete_payload.promptVersion == "diagnosis-prompt-set-v1"

    analysis_metadata = json.loads(complete_payload.analysisMetadata or "{}")
    assert analysis_metadata["pipelineVersion"] == "ai-diagnosis-v1"
    assert analysis_metadata["promptSetVersion"] == "diagnosis-prompt-set-v1"

    assert len(complete_payload.jobs) == 2
    assert complete_payload.jobs[0].jdId == 10
    assert complete_payload.jobs[0].rankOrder == 1
    assert complete_payload.jobs[0].fitScore > complete_payload.jobs[1].fitScore

    top_job_match_details = json.loads(complete_payload.jobs[0].matchDetails or "[]")
    assert [match["status"] for match in top_job_match_details] == [
        "matched",
        "matched",
    ]
    assert (
        top_job_match_details[0]["evidence"][0]["evidence"]["sourceType"]
        == "project"
    )

    dumped_result = result.model_dump(mode="json")
    assert dumped_result["reportPackage"]["jobs"][0]["jdId"] == 10
