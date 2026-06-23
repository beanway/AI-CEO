"""相容層：請改從 ai_company.schemas.documents 匯入。"""

from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    NotificationPolicy,
    ProjectRecord,
    ProjectSkillsFile,
    ProjectsFile,
    SessionRecord,
    UserMode,
    UserPref,
    UserPrefsFile,
    WorkerEntry,
    WorkersFile,
    utc_now,
)

__all__ = [
    "GlobalConfigFile",
    "GlobalSkillsFile",
    "NotificationPolicy",
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
