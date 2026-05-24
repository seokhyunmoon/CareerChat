from __future__ import annotations

from collections import Counter
from typing import Any

from app.prototype.clients.embedding_client import get_embeddings
from app.prototype.clients.llm_client import get_llm
from app.prototype.services.job_structuring_service import (
    normalize_requirement_tags,
    structure_job_posting,
)
from app.prototype.services.matching_service import match_requirements
from app.prototype.services.profile_document_service import build_profile_documents
from app.prototype.services.report_service import build_report_input, generate_report
from app.prototype.services.retrieval_service import create_retriever, selective_split_profile_docs
from app.prototype.services.scoring_service import compute_fit_score


def analyze_jobs(
    user: dict[str, Any],
    profile: dict[str, Any],
    education: list[dict[str, Any]],
    work_experience: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    achievements: list[dict[str, Any]],
    job_postings: list[dict[str, Any]],
    top_k: int = 3,
    llm: Any | None = None,
    embeddings: Any | None = None,
) -> dict[str, Any]:
    llm = llm or get_llm()
    embeddings = embeddings or get_embeddings()

    profile_docs = build_profile_documents(
        user=user,
        profile=profile,
        education=education,
        work_experience=work_experience,
        projects=projects,
        achievements=achievements,
    )
    profile_chunks = selective_split_profile_docs(profile_docs)
    retriever = create_retriever(profile_chunks, embeddings, top_k=top_k)

    active_jobs = [
        job for job in job_postings if job.get("company_name") and job.get("content")
    ]
    analyses = []

    for job in active_jobs:
        structured_job = structure_job_posting(job, llm)
        structured_job = normalize_requirement_tags(structured_job)
        matches = match_requirements(
            requirements=structured_job.requirements,
            retriever=retriever,
            llm=llm,
            top_k=top_k,
        )
        score_info = compute_fit_score(matches)

        analyses.append(
            {
                "company": structured_job.company_name,
                "position": structured_job.position,
                "score": score_info["fit_score"],
                "score_info": score_info,
                "matches": matches,
                "structured_data": structured_job,
            }
        )

    analyses.sort(key=lambda analysis: analysis["score"], reverse=True)

    if not analyses:
        return {
            "profile_document_count": len(profile_docs),
            "profile_chunk_count": len(profile_chunks),
            "rankings": [],
            "best_result": None,
            "match_summary": None,
            "report_input": None,
            "final_report": None,
        }

    best_result = analyses[0]
    best_matches = best_result["matches"]
    best_structured_job = best_result["structured_data"]
    best_score_result = best_result["score_info"]

    match_counter = Counter(match.match_level for match in best_matches)
    importance_counter = Counter(
        f"{match.importance}:{match.match_level}" for match in best_matches
    )

    report_input = build_report_input(
        structured_job=best_structured_job,
        matches=best_matches,
        score_result=best_score_result,
    )
    final_report = generate_report(report_input, llm)

    return {
        "profile_document_count": len(profile_docs),
        "profile_chunk_count": len(profile_chunks),
        "rankings": [_serialize_analysis(analysis) for analysis in analyses],
        "best_result": _serialize_analysis(best_result),
        "match_summary": {
            "match_level_counts": dict(match_counter),
            "importance_match_counts": dict(importance_counter),
        },
        "report_input": report_input,
        "final_report": final_report,
    }


def _serialize_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "company": analysis["company"],
        "position": analysis["position"],
        "score": analysis["score"],
        "score_info": analysis["score_info"],
        "matches": [_dump_model(match) for match in analysis["matches"]],
        "structured_data": _dump_model(analysis["structured_data"]),
    }


def _dump_model(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()

    return value
