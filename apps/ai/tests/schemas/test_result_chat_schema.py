from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.result_chat import (
    ResultChatEvidenceData,
    ResultChatResponseRequest,
)


def build_result_chat_request_body() -> dict:
    return {
        "diagnosisId": 1,
        "userMessage": "어느 공고를 먼저 지원하는 게 좋아?",
        "reportSummary": "토스 공고가 가장 적합합니다.",
        "reportContent": "# 분석 리포트\n토스 공고의 적합도가 가장 높습니다.",
        "jobResults": [
            {
                "jdId": 10,
                "rankOrder": 1,
                "companyName": "토스",
                "position": "AI Engineer",
                "fitScore": 82.5,
                "strengthsSummary": "RAG 설계 경험이 강점입니다.",
                "gapsSummary": "제품화 경험 보완이 필요합니다.",
                "highlightPoints": ["RAG", "LLM reranking"],
                "matchDetails": [{"requirement": {"description": "RAG 경험"}}],
            }
        ],
        "previousMessages": [
            {
                "role": "USER",
                "content": "강점이 뭐야?",
            }
        ],
    }


def test_result_chat_request_accepts_diagnosis_result_context() -> None:
    request = ResultChatResponseRequest.model_validate(build_result_chat_request_body())

    assert request.diagnosisId == 1
    assert request.userMessage == "어느 공고를 먼저 지원하는 게 좋아?"
    assert request.jobResults[0].jdId == 10
    assert request.jobResults[0].highlightPoints == ["RAG", "LLM reranking"]
    assert request.previousMessages[0].role == "USER"


def test_result_chat_request_rejects_duplicate_job_results() -> None:
    body = build_result_chat_request_body()
    body["jobResults"].append(
        {
            **body["jobResults"][0],
            "rankOrder": 2,
        }
    )

    with pytest.raises(ValidationError, match="duplicate jdId"):
        ResultChatResponseRequest.model_validate(body)


def test_result_chat_evidence_rejects_duplicate_referenced_jobs() -> None:
    with pytest.raises(ValidationError, match="duplicate"):
        ResultChatEvidenceData(
            referencedJobIds=[10, 10],
            reasonCodes=["FIT_SCORE"],
            usedFields=["jobResults.fitScore"],
        )
