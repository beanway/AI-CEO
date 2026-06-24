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
    executor_notify_chat_id: int | None = None
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


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ExecutionStateFile(BaseModel):
    """Phase B 執行狀態檔（P-A3 維修 flow 可讀寫中斷）。"""

    execution_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    worker_id: str | None = None
    status: ExecutionStatus = ExecutionStatus.RUNNING
    updated_at: datetime = Field(default_factory=utc_now)
    failure_reason: str | None = None


class ExecutionQueueItem(BaseModel):
    """全公司單一佇列中的一筆派工。"""

    project_id: str = Field(min_length=1)
    worker_id: str = Field(min_length=1)
    enqueued_at: datetime = Field(default_factory=utc_now)


class ExecutionQueueFile(BaseModel):
    """`_company/execution/queue.json`：待執行派工（同時僅一筆 RUNNING execution）。"""

    pending: list[ExecutionQueueItem] = Field(default_factory=list)


class ProjectLifecycle(str, Enum):
    ACTIVE = "active"
    PROJECT_DONE = "project_done"


class ProjectHarnessStateFile(BaseModel):
    """專案 harness 狀態：`projects/<id>/pm/harness_state.json`。"""

    lifecycle: ProjectLifecycle = ProjectLifecycle.ACTIVE
    last_completed_worker_id: str | None = None


class ExecutionFailureDecision(str, Enum):
    RETRY = "retry"
    CODE_REVIEW = "code_review"


class PendingExecutionFailureRecord(BaseModel):
    id: str = Field(min_length=1)
    execution_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    worker_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision: ExecutionFailureDecision | None = None
    created_at: datetime = Field(default_factory=utc_now)


class PendingExecutionFailuresFile(BaseModel):
    items: dict[str, PendingExecutionFailureRecord] = Field(default_factory=dict)


__all__ = [
    "ApprovalKind",
    "ApprovalStatus",
    "ExecutionFailureDecision",
    "ExecutionQueueFile",
    "ExecutionQueueItem",
    "ExecutionStateFile",
    "ExecutionStatus",
    "PendingExecutionFailureRecord",
    "PendingExecutionFailuresFile",
    "ProjectHarnessStateFile",
    "ProjectLifecycle",
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
