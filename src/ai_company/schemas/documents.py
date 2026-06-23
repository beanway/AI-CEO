"""
Document DTOs: on-disk JSON/YAML contracts.

When changing files under company_workspace/_company/, update models here first,
then the single writer module (target: modules/file_store).
"""

from ai_company.models.company import (
    GlobalConfigFile,
    GlobalSkillsFile,
    ProjectRecord,
    ProjectsFile,
    SessionRecord,
    UserMode,
    UserPref,
    UserPrefsFile,
)

__all__ = [
    "GlobalConfigFile",
    "GlobalSkillsFile",
    "ProjectRecord",
    "ProjectsFile",
    "SessionRecord",
    "UserMode",
    "UserPref",
    "UserPrefsFile",
]
