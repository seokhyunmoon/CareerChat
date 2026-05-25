"""Schemas for AI backend request, response, callback, and metadata contracts."""

from app.schemas.analysis_job import (
    AnalysisJobCreateResponse,
    AnalysisJobPosting,
    AnalysisJobRequest,
    CallbackTarget,
)
from app.schemas.analysis_result import (
    AnalysisReportPackage,
    JobAnalysisResult,
    JobRequirement,
    MatchedProfileEvidence,
    RequirementMatch,
)
from app.schemas.callback import (
    CompleteCallbackJobResult,
    CompleteCallbackPayload,
    FailCallbackPayload,
)
from app.schemas.metadata import AnalysisMetadata, AnalysisStepMetadata, ErrorDetails
from app.schemas.profile_snapshot import (
    AchievementSnapshot,
    EducationSnapshot,
    ProfileEvidenceReference,
    ProfileSnapshot,
    ProjectSnapshot,
    SnapshotProfile,
    WorkExperienceSnapshot,
)

__all__ = [
    "AchievementSnapshot",
    "AnalysisJobCreateResponse",
    "AnalysisJobPosting",
    "AnalysisJobRequest",
    "AnalysisMetadata",
    "AnalysisReportPackage",
    "AnalysisStepMetadata",
    "CallbackTarget",
    "CompleteCallbackJobResult",
    "CompleteCallbackPayload",
    "EducationSnapshot",
    "ErrorDetails",
    "FailCallbackPayload",
    "JobAnalysisResult",
    "JobRequirement",
    "MatchedProfileEvidence",
    "ProfileEvidenceReference",
    "ProfileSnapshot",
    "ProjectSnapshot",
    "RequirementMatch",
    "SnapshotProfile",
    "WorkExperienceSnapshot",
]
