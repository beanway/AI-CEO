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
    """CEO：全專案預設（模型、通知政策）。"""

    default_model: str = "gemini-2.5-flash"
    notification_policy: NotificationPolicy = NotificationPolicy.ALL
