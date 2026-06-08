from __future__ import annotations

import json
from collections.abc import Sequence

from app.llm.provider import PromptExecutionRequest
from app.prompts.manifest import (
    JOB_STRUCTURING_PROMPT,
    REPORT_GENERATION_PROMPT,
    REQUIREMENT_MATCHING_PROMPT,
    PromptDefinition,
)
from app.prompts.renderer import render_prompt_template
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
)
from app.schemas.result_chat import ResultChatResponseRequest


RESULT_CHAT_RESPONSE_PROMPT_KEY = "result_chat_response"
RESULT_CHAT_RESPONSE_PROMPT_VERSION = "result-chat-response-v1"
RESULT_CHAT_RESPONSE_TEMPLATE_PATH = "result_chat_response_v1.md"

def build_job_structuring_prompt(
    *,
    job: AnalysisJobPosting,
    model_name: str,
    temperature: float | None = None,
    definition: PromptDefinition = JOB_STRUCTURING_PROMPT,
) -> PromptExecutionRequest:
    payload = {
        "job": job.model_dump(mode="json"),
        "outputSchema": {
            "requirements": [
                {
                    "requirementId": f"jd-{job.jdId}-req-1",
                    "category": (
                        "skill | experience | qualification | responsibility | "
                        "preference | other"
                    ),
                    "priority": "required | preferred | optional",
                    "description": "요구사항을 한 문장으로 정규화",
                    "keywords": ["핵심 키워드"],
                    "sourceText": "공고 원문에서 근거가 되는 문장",
                }
            ]
        },
    }

    prompt_template = render_prompt_template(
        definition.template_path,
        {"payload_json": _dump_prompt_json(payload)},
    )

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt=prompt_template.system_prompt,
        userPrompt=prompt_template.user_prompt,
        responseSchemaName="JobRequirementsOutput",
        temperature=temperature,
        metadata={"jdId": job.jdId},
    )


def build_requirement_matching_prompt(
    *,
    job: AnalysisJobPosting,
    requirement: JobRequirement,
    evidence: Sequence[MatchedProfileEvidence],
    model_name: str,
    temperature: float | None = None,
    definition: PromptDefinition = REQUIREMENT_MATCHING_PROMPT,
) -> PromptExecutionRequest:
    payload = {
        "job": {
            "jdId": job.jdId,
            "companyName": job.companyName,
            "position": job.position,
        },
        "requirement": requirement.model_dump(mode="json"),
        "evidence": [
            {
                "index": index,
                "item": item.model_dump(mode="json"),
            }
            for index, item in enumerate(evidence)
        ],
        "outputSchema": {
            "status": "matched | partial | missing",
            "confidenceScore": "0.0부터 1.0까지의 숫자",
            "evidenceIndexes": [0],
            "rationale": "판단 근거",
            "gap": "partial 또는 missing일 때 보완할 내용, matched이면 null",
        },
    }

    prompt_template = render_prompt_template(
        definition.template_path,
        {"payload_json": _dump_prompt_json(payload)},
    )

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt=prompt_template.system_prompt,
        userPrompt=prompt_template.user_prompt,
        responseSchemaName="RequirementMatchDecision",
        temperature=temperature,
        metadata={"jdId": job.jdId, "requirementId": requirement.requirementId},
    )


def build_report_generation_prompt(
    *,
    job_results: Sequence[JobAnalysisResult],
    model_name: str,
    temperature: float | None = None,
    definition: PromptDefinition = REPORT_GENERATION_PROMPT,
) -> PromptExecutionRequest:
    payload = {
        "jobs": [
            {
                "jdId": job.jdId,
                "rankOrder": job.rankOrder,
                "companyName": job.companyName,
                "position": job.position,
                "fitScore": job.fitScore,
                "requirementMatches": [
                    match.model_dump(mode="json")
                    for match in job.requirementMatches
                ],
            }
            for job in job_results
        ],
        "outputSchema": {
            "reportSummary": "전체 결과 한두 문장 요약",
            "reportContent": "Markdown 형식의 상세 리포트",
            "jobs": [
                {
                    "jdId": 1,
                    "strengthsSummary": "공고별 강점 요약",
                    "gapsSummary": "공고별 보완점 요약",
                    "highlightPoints": ["강조할 키워드"],
                }
            ],
        },
    }

    prompt_template = render_prompt_template(
        definition.template_path,
        {"payload_json": _dump_prompt_json(payload)},
    )

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt=prompt_template.system_prompt,
        userPrompt=prompt_template.user_prompt,
        responseSchemaName="ReportGenerationOutput",
        temperature=temperature,
        metadata={"jobCount": len(job_results)},
    )


def build_result_chat_response_prompt(
    *,
    request: ResultChatResponseRequest,
    model_name: str,
    temperature: float | None = None,
) -> PromptExecutionRequest:
    payload = {
        "diagnosisId": request.diagnosisId,
        "userMessage": request.userMessage,
        "reportSummary": request.reportSummary,
        "reportContent": request.reportContent,
        "jobResults": [
            job.model_dump(mode="json")
            for job in request.jobResults
        ],
        "previousMessages": [
            message.model_dump(mode="json")
            for message in request.previousMessages
        ],
        "outputSchema": {
            "content": "사용자에게 보여줄 한국어 답변",
            "referencedJobIds": [request.jobResults[0].jdId],
            "reasonCodes": ["REPORT_SUMMARY"],
            "usedFields": ["reportSummary"],
        },
    }

    prompt_template = render_prompt_template(
        RESULT_CHAT_RESPONSE_TEMPLATE_PATH,
        {"payload_json": _dump_prompt_json(payload)},
    )

    return PromptExecutionRequest(
        promptKey=RESULT_CHAT_RESPONSE_PROMPT_KEY,
        promptVersion=RESULT_CHAT_RESPONSE_PROMPT_VERSION,
        modelName=model_name,
        systemPrompt=prompt_template.system_prompt,
        userPrompt=prompt_template.user_prompt,
        responseSchemaName="ResultChatResponseOutput",
        temperature=temperature,
        metadata={
            "diagnosisId": request.diagnosisId,
            "jobCount": len(request.jobResults),
            "previousMessageCount": len(request.previousMessages),
        },
    )


def _dump_prompt_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
