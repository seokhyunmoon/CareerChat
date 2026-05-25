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
from app.schemas.analysis_job import AnalysisJobPosting
from app.schemas.analysis_result import (
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
)

JSON_OUTPUT_RULES = "\n".join(
    [
        "응답은 Markdown code block 없이 순수 JSON object만 반환한다.",
        "설명 문장, 주석, trailing comma를 JSON 밖에 추가하지 않는다.",
        "입력에 없는 프로필 근거, 회사 정보, 성과 수치를 새로 만들지 않는다.",
    ]
)


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

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt="\n".join(
            [
                "너는 개발자 채용공고를 분석해 요구사항을 구조화하는 채용 분석가다.",
                "요구사항은 최대 12개로 묶고, 같은 의미의 항목은 중복 생성하지 않는다.",
                JSON_OUTPUT_RULES,
            ]
        ),
        userPrompt=_dump_prompt_json(payload),
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

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt="\n".join(
            [
                "너는 개발자 이력과 채용공고 요구사항의 적합도를 판단하는 분석가다.",
                "evidenceIndexes에는 입력 evidence 배열에 존재하는 index만 넣는다.",
                "missing 상태에서는 evidenceIndexes를 빈 배열로 둔다.",
                JSON_OUTPUT_RULES,
            ]
        ),
        userPrompt=_dump_prompt_json(payload),
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

    return PromptExecutionRequest(
        promptKey=definition.key,
        promptVersion=definition.version,
        modelName=model_name,
        systemPrompt="\n".join(
            [
                "너는 개발자 취업 준비생에게 공고별 지원 전략을 설명하는 커리어 분석가다.",
                "입력된 match 결과와 점수만 근거로 사용하고 새로운 경험을 만들지 않는다.",
                "reportContent는 사용자에게 바로 보여줄 수 있는 Markdown으로 작성한다.",
                JSON_OUTPUT_RULES,
            ]
        ),
        userPrompt=_dump_prompt_json(payload),
        responseSchemaName="ReportGenerationOutput",
        temperature=temperature,
        metadata={"jobCount": len(job_results)},
    )


def _dump_prompt_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
