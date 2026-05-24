from __future__ import annotations

from typing import Any

from langchain_core.documents import Document


def build_profile_documents(
    user: dict[str, Any],
    profile: dict[str, Any],
    education: list[dict[str, Any]],
    work_experience: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    achievements: list[dict[str, Any]],
) -> list[Document]:
    documents = []

    overview_text = f"""
[기본 정보]
이름: {user['name']}
이메일: {user['email']}
전화번호: {user['telephone']}
지원 유형: {profile['experience_level']}
    """.strip()

    documents.append(
        Document(
            page_content=overview_text,
            metadata={
                "type": "profile_overview",
                "profile_id": profile["profile_id"],
                "title": user["name"],
            },
        )
    )

    for edu in education:
        if edu["profile_id"] != profile["profile_id"]:
            continue

        edu_text = f"""
[학력]
학교명: {edu['school_name']}
졸업 상태: {edu['grad_status']}
학위: {edu['degree']}
전공: {edu['major']}
기간: {edu['start_date']} ~ {edu['end_date']}
        """.strip()

        documents.append(
            Document(
                page_content=edu_text,
                metadata={
                    "type": "education",
                    "profile_id": profile["profile_id"],
                    "title": edu["school_name"],
                },
            )
        )

    for exp in work_experience:
        if exp["profile_id"] != profile["profile_id"]:
            continue

        exp_text = f"""
[경력]
회사명: {exp['company_name']}
고용형태: {exp['employment_type']}
직무: {exp['position']}
기간: {exp['start_date']} ~ {exp['end_date']}
설명:
{exp['description']}
        """.strip()

        documents.append(
            Document(
                page_content=exp_text,
                metadata={
                    "type": "work_experience",
                    "profile_id": profile["profile_id"],
                    "title": exp["company_name"],
                },
            )
        )

    for project in projects:
        if project["profile_id"] != profile["profile_id"]:
            continue

        project_text = f"""
[프로젝트]
프로젝트명: {project['project_name']}
설명:
{project['description']}
        """.strip()

        documents.append(
            Document(
                page_content=project_text,
                metadata={
                    "type": "project",
                    "profile_id": profile["profile_id"],
                    "title": project["project_name"],
                },
            )
        )

    for achievement in achievements:
        if achievement["profile_id"] != profile["profile_id"]:
            continue

        achievement_text = f"""
[성과/자격]
이름: {achievement['title']}
발급기관: {achievement['issuer']}
점수/등급: {achievement['score_or_grade']}
취득일: {achievement['acquired_date']}
        """.strip()

        documents.append(
            Document(
                page_content=achievement_text,
                metadata={
                    "type": "achievement",
                    "profile_id": profile["profile_id"],
                    "title": achievement["title"],
                },
            )
        )

    return documents
