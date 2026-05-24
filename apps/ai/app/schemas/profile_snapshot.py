from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SnapshotProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profileId: int
    experienceLevel: str | None = None


class EducationSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    educationId: int | None = None
    schoolName: str | None = None
    gradStatus: str | None = None
    degree: str | None = None
    major: str | None = None
    startDate: str | None = None
    endDate: str | None = None


class WorkExperienceSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    workExperienceId: int | None = None
    companyName: str | None = None
    employmentType: str | None = None
    position: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    description: str | None = None


class ProjectSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    projectId: int | None = None
    projectName: str | None = None
    description: str | None = None


class AchievementSnapshot(BaseModel):
    model_config = ConfigDict(extra="allow")

    achievementId: int | None = None
    title: str | None = None
    issuer: str | None = None
    scoreOrGrade: str | None = None
    acquiredDate: str | None = None


class ProfileSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshotVersion: int = Field(ge=1)
    profile: SnapshotProfile
    education: list[EducationSnapshot] = Field(default_factory=list)
    workExperiences: list[WorkExperienceSnapshot] = Field(default_factory=list)
    projects: list[ProjectSnapshot] = Field(default_factory=list)
    achievements: list[AchievementSnapshot] = Field(default_factory=list)


class ProfileEvidenceReference(BaseModel):
    sourceType: Literal[
        "education",
        "work_experience",
        "project",
        "achievement",
        "profile_overview",
    ]
    sourceId: int | str | None = None
    chunkIndex: int = Field(default=0, ge=0)
    title: str | None = None
    text: str | None = None


ALLOWED_PROFILE_SNAPSHOT_KEYS: frozenset[str] = frozenset(
    {
        "snapshotVersion",
        "profile",
        "education",
        "workExperiences",
        "projects",
        "achievements",
    }
)

PII_PROFILE_KEYS: frozenset[str] = frozenset(
    {
        "name",
        "email",
        "telephone",
        "phone",
        "password",
        "passwordHash",
    }
)


def find_disallowed_profile_keys(payload: dict[str, Any]) -> set[str]:
    return set(payload) - ALLOWED_PROFILE_SNAPSHOT_KEYS


def find_pii_profile_keys(payload: dict[str, Any]) -> set[str]:
    found = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested_value in value.items():
                if key in PII_PROFILE_KEYS:
                    found.add(key)
                visit(nested_value)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    return found
