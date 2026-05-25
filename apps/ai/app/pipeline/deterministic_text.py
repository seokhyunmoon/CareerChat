from __future__ import annotations

import re
from collections.abc import Iterable

KNOWN_MATCH_TERMS: tuple[str, ...] = (
    "spring boot",
    "rest api",
    "node.js",
    "typescript",
    "javascript",
    "postgresql",
    "fastapi",
    "langchain",
    "qdrant",
    "redis",
    "celery",
    "docker",
    "react",
    "spring",
    "python",
    "java",
    "jpa",
    "jwt",
    "oauth",
    "mysql",
    "sql",
    "aws",
    "api",
    "rag",
    "llm",
    "백엔드",
    "프론트엔드",
    "데이터베이스",
    "협업",
    "배포",
    "운영",
    "설계",
    "테스트",
)

STOP_TERMS: frozenset[str] = frozenset(
    {
        "and",
        "or",
        "the",
        "with",
        "for",
        "required",
        "preferred",
        "experience",
        "project",
        "description",
        "경험",
        "개발",
        "필수",
        "우대",
        "자격",
        "요건",
        "담당",
        "업무",
        "프로젝트",
        "프로젝트명",
        "설명",
        "경력",
        "직무",
    }
)

TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9+.#-]*|[가-힣]{2,}")


def extract_match_terms(*values: object | None) -> list[str]:
    text = _normalize_text(" ".join(str(value) for value in values if value))
    if not text:
        return []

    terms = set()
    for known_term in KNOWN_MATCH_TERMS:
        if known_term in text:
            terms.add(known_term)

    for token in TOKEN_PATTERN.findall(text):
        normalized = _normalize_token(token)
        if normalized and normalized not in STOP_TERMS:
            terms.add(normalized)

    return sorted(terms)


def calculate_term_relevance(
    query_terms: Iterable[str],
    target_text: str,
) -> float:
    normalized_query_terms = {term for term in query_terms if term}
    if not normalized_query_terms:
        return 0.0

    target_terms = set(extract_match_terms(target_text))
    if not target_terms:
        return 0.0

    matched_terms = normalized_query_terms.intersection(target_terms)
    return len(matched_terms) / len(normalized_query_terms)


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _normalize_token(token: str) -> str | None:
    normalized = token.lower().strip("-_.")
    if not normalized:
        return None
    if len(normalized) > 3 and normalized.endswith("s"):
        normalized = normalized[:-1]
    return normalized
