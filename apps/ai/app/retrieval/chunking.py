from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.retrieval.chunks import ProfileChunkSourceType, ProfileSnapshotChunk
from app.schemas.profile_snapshot import (
    ProfileEvidenceReference,
    ProfileSnapshot,
    find_disallowed_profile_keys,
    find_pii_profile_keys,
)

MAX_CHUNK_TEXT_LENGTH = 800
CHUNK_OVERLAP = 120

LabeledTextPart = tuple[str, object | None]


def build_safe_profile_snapshot_chunks(
    diagnosis_id: int,
    payload: dict[str, Any],
    *,
    max_chunk_text_length: int = MAX_CHUNK_TEXT_LENGTH,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[ProfileSnapshotChunk]:
    disallowed_keys = find_disallowed_profile_keys(payload)
    if disallowed_keys:
        keys = ", ".join(sorted(disallowed_keys))
        raise ValueError(f"profile snapshot contains disallowed keys: {keys}")

    pii_keys = find_pii_profile_keys(payload)
    if pii_keys:
        keys = ", ".join(sorted(pii_keys))
        raise ValueError(f"profile snapshot contains PII keys: {keys}")

    snapshot = ProfileSnapshot.model_validate(payload)
    return build_profile_snapshot_chunks(
        diagnosis_id=diagnosis_id,
        snapshot=snapshot,
        max_chunk_text_length=max_chunk_text_length,
        chunk_overlap=chunk_overlap,
    )


def build_profile_snapshot_chunks(
    diagnosis_id: int,
    snapshot: ProfileSnapshot,
    *,
    max_chunk_text_length: int = MAX_CHUNK_TEXT_LENGTH,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[ProfileSnapshotChunk]:
    _validate_split_config(max_chunk_text_length, chunk_overlap)

    chunks: list[ProfileSnapshotChunk] = []
    metadata = {"snapshotVersion": snapshot.snapshotVersion}

    overview_body = _format_labeled_text(
        ("경력 수준", snapshot.profile.experienceLevel),
    )
    if overview_body:
        chunks.extend(
            _build_source_chunks(
                diagnosis_id=diagnosis_id,
                source_type="profile_overview",
                source_id=snapshot.profile.profileId,
                title="프로필 요약",
                context_text="프로필 요약.",
                body_text=overview_body,
                metadata=metadata,
                max_chunk_text_length=max_chunk_text_length,
                chunk_overlap=chunk_overlap,
            )
        )

    for education in snapshot.education:
        chunks.extend(
            _build_source_chunks(
                diagnosis_id=diagnosis_id,
                source_type="education",
                source_id=education.educationId,
                title=education.schoolName,
                context_text=_format_context("학교명", education.schoolName, "학력"),
                body_text=_format_labeled_text(
                    ("전공", education.major),
                    ("학위", education.degree),
                    ("졸업 상태", education.gradStatus),
                    ("기간", _date_range(education.startDate, education.endDate)),
                ),
                metadata=metadata,
                max_chunk_text_length=max_chunk_text_length,
                chunk_overlap=chunk_overlap,
            )
        )

    for work_experience in snapshot.workExperiences:
        chunks.extend(
            _build_source_chunks(
                diagnosis_id=diagnosis_id,
                source_type="work_experience",
                source_id=work_experience.workExperienceId,
                title=work_experience.companyName,
                context_text=_format_context(
                    "회사명",
                    work_experience.companyName,
                    "경력",
                ),
                body_text=_format_labeled_text(
                    ("직무", work_experience.position),
                    ("고용 형태", work_experience.employmentType),
                    (
                        "기간",
                        _date_range(
                            work_experience.startDate,
                            work_experience.endDate,
                        ),
                    ),
                    ("설명", work_experience.description),
                ),
                metadata=metadata,
                max_chunk_text_length=max_chunk_text_length,
                chunk_overlap=chunk_overlap,
            )
        )

    for project in snapshot.projects:
        chunks.extend(
            _build_source_chunks(
                diagnosis_id=diagnosis_id,
                source_type="project",
                source_id=project.projectId,
                title=project.projectName,
                context_text=_format_context("프로젝트명", project.projectName, "프로젝트"),
                body_text=_format_labeled_text(("설명", project.description)),
                metadata=metadata,
                max_chunk_text_length=max_chunk_text_length,
                chunk_overlap=chunk_overlap,
            )
        )

    for achievement in snapshot.achievements:
        chunks.extend(
            _build_source_chunks(
                diagnosis_id=diagnosis_id,
                source_type="achievement",
                source_id=achievement.achievementId,
                title=achievement.title,
                context_text=_format_context("성과명", achievement.title, "성과"),
                body_text=_format_labeled_text(
                    ("발급 기관", achievement.issuer),
                    ("점수 또는 등급", achievement.scoreOrGrade),
                    ("취득일", achievement.acquiredDate),
                ),
                metadata=metadata,
                max_chunk_text_length=max_chunk_text_length,
                chunk_overlap=chunk_overlap,
            )
        )

    return chunks


def _build_source_chunks(
    *,
    diagnosis_id: int,
    source_type: ProfileChunkSourceType,
    source_id: int | str | None,
    title: str | None,
    context_text: str,
    body_text: str,
    metadata: dict[str, int],
    max_chunk_text_length: int,
    chunk_overlap: int,
) -> list[ProfileSnapshotChunk]:
    source_texts = _split_with_context(
        context_text=context_text,
        body_text=body_text,
        max_chunk_text_length=max_chunk_text_length,
        chunk_overlap=chunk_overlap,
    )

    return [
        _build_chunk(
            diagnosis_id=diagnosis_id,
            source_type=source_type,
            source_id=source_id,
            chunk_index=chunk_index,
            title=title,
            text=text,
            metadata=metadata,
        )
        for chunk_index, text in enumerate(source_texts)
    ]


def _build_chunk(
    *,
    diagnosis_id: int,
    source_type: ProfileChunkSourceType,
    source_id: int | str | None,
    chunk_index: int,
    title: str | None,
    text: str,
    metadata: dict[str, int],
) -> ProfileSnapshotChunk:
    chunk_id = _build_chunk_id(
        diagnosis_id=diagnosis_id,
        source_type=source_type,
        source_id=source_id,
        chunk_index=chunk_index,
    )

    return ProfileSnapshotChunk(
        diagnosis_id=diagnosis_id,
        chunk_id=chunk_id,
        text=text,
        evidence=ProfileEvidenceReference(
            sourceType=source_type,
            sourceId=source_id,
            chunkIndex=chunk_index,
            title=title,
            text=text,
        ),
        metadata=metadata,
    )


def _build_chunk_id(
    *,
    diagnosis_id: int,
    source_type: ProfileChunkSourceType,
    source_id: int | str | None,
    chunk_index: int,
) -> str:
    normalized_source_id = source_id if source_id is not None else "unknown"
    return f"diagnosis-{diagnosis_id}-{source_type}-{normalized_source_id}-{chunk_index}"


def _split_with_context(
    *,
    context_text: str,
    body_text: str,
    max_chunk_text_length: int,
    chunk_overlap: int,
) -> list[str]:
    context = _normalize_text(context_text)
    body = _normalize_text(body_text)
    full_text = _join_sentences(context, body)

    if not full_text:
        return []
    if len(full_text) <= max_chunk_text_length:
        return [full_text]
    if not context:
        return _split_text_with_recursive_splitter(
            full_text,
            chunk_size=max_chunk_text_length,
            chunk_overlap=chunk_overlap,
        )

    body_max_length = max_chunk_text_length - len(context) - 1
    if body_max_length <= 0:
        return _split_text_with_recursive_splitter(
            full_text,
            chunk_size=max_chunk_text_length,
            chunk_overlap=chunk_overlap,
        )

    body_chunks = _split_text_with_recursive_splitter(
        body,
        chunk_size=body_max_length,
        chunk_overlap=chunk_overlap,
    )
    if not body_chunks:
        return [context]

    return [_join_sentences(context, body_chunk) for body_chunk in body_chunks]


def _split_text_with_recursive_splitter(
    text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        keep_separator="end",
        separators=["\n\n", "\n", ". ", "? ", "! ", "。", " ", ""],
    )
    return [chunk.strip() for chunk in splitter.split_text(normalized) if chunk.strip()]


def _format_context(label: str, value: object | None, fallback: str) -> str:
    normalized = _normalize_text(value)
    if normalized:
        return _format_labeled_text((label, normalized))
    return _ensure_sentence(fallback)


def _format_labeled_text(*parts: LabeledTextPart) -> str:
    sentences = []
    for label, value in parts:
        normalized = _normalize_text(value)
        if normalized:
            sentences.append(f"{label}: {_ensure_sentence(normalized)}")
    return " ".join(sentences)


def _join_sentences(*parts: str | None) -> str:
    return " ".join(part for part in parts if part)


def _normalize_text(value: object | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(str(value).split())
    return normalized or None


def _ensure_sentence(text: str) -> str:
    if text.endswith((".", "?", "!", "。")):
        return text
    return f"{text}."


def _date_range(start_date: str | None, end_date: str | None) -> str | None:
    if start_date and end_date:
        return f"{start_date} ~ {end_date}"
    return start_date or end_date


def _validate_split_config(max_chunk_text_length: int, chunk_overlap: int) -> None:
    if max_chunk_text_length < 1:
        raise ValueError("max_chunk_text_length must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= max_chunk_text_length:
        raise ValueError("chunk_overlap must be smaller than max_chunk_text_length")
