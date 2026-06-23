"""
Document DTOs: on-disk JSON/YAML contracts.

When changing files under company_workspace/_company/, update models here first,
then the single writer module (target: modules/file_store).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectRecord(BaseModel):
    id: str
    name: str
    created_at: datetime = Field(default_factory=utc_now)
    status: str = "active"


class ProjectsFile(BaseModel):
    active_project_id: str | None = None
    projects: list[ProjectRecord] = Field(default_factory=list)


class UserMode(str, Enum):
    CEO = "ceo"
    PM = "pm"


class UserPref(BaseModel):
    mode: UserMode = UserMode.CEO


class UserPrefsFile(BaseModel):
    users: dict[str, UserPref] = Field(default_factory=dict)


class SessionRecord(BaseModel):
    gemini_chat_name: str
    project_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    stale: bool = False


class GlobalSkillsFile(BaseModel):
    """CEO：全專案啟用的 skills/registry skill id。"""

    enabled_skill_ids: list[str] = Field(default_factory=list)


class NotificationPolicy(str, Enum):
    ALL = "all"
    FAILURES_ONLY = "failures_only"
    OFF = "off"


class GlobalConfigFile(BaseModel):
    """CEO：全專案預設（模型、通知政策、AI 生成）。"""

    default_model: str = "gemini-2.5-flash"
    notification_policy: NotificationPolicy = NotificationPolicy.ALL
    max_output_tokens: int = Field(default=8192, ge=1)
    thinking_budget: int = 0
    include_thoughts: bool = False
    temperature: float | None = None


class WorkerEntry(BaseModel):
    id: str = Field(min_length=1)
    kind: str = Field(min_length=1)


class WorkersFile(BaseModel):
    workers: list[WorkerEntry] = Field(default_factory=list)


class ProjectSkillsFile(BaseModel):
    """PM：本專案全角色共用的 registry skill id。"""

    enabled_skill_ids: list[str] = Field(default_factory=list)


class ApprovalKind(str, Enum):
    PROJECT_GIT = "project_git"
    ADD_SKILL_TO_PROJECT = "add_skill_to_project"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    REJECTED = "rejected"
    COMPLETED = "completed"


class PendingApprovalRecord(BaseModel):
    id: str = Field(min_length=1)
    kind: ApprovalKind
    project_id: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    channel: str = "cli"
    requester_telegram_id: int | None = None
    git_argv: list[str] | None = None
    skill_id: str | None = None


class PendingApprovalsFile(BaseModel):
    items: dict[str, PendingApprovalRecord] = Field(default_factory=dict)


__all__ = [
    "ApprovalKind",
    "ApprovalStatus",
    "GlobalConfigFile",
    "GlobalSkillsFile",
    "NotificationPolicy",
    "PendingApprovalRecord",
    "PendingApprovalsFile",
    "ApprovalKind",
    "ApprovalStatus",
    "ProjectRecord",
    "ProjectSkillsFile",
    "ProjectsFile",
    "SessionRecord",
    "UserMode",
    "UserPref",
    "UserPrefsFile",
    "WorkerEntry",
    "WorkersFile",
    "utc_now",
]
