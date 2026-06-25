"""工作區路徑常數與純函式（模組共用，避免重複 project_dir）。"""

from __future__ import annotations

from pathlib import Path

COMPANY_DIR_NAME = "_company"
PROJECTS_DIR_NAME = "projects"
DEFAULT_WORKSPACE_DIR_NAME = "company_workspace"


def framework_repo_root() -> Path:
    """本框架 repo 根（含 `src/`、`company_workspace/`）。"""
    return Path(__file__).resolve().parents[3]


def resolve_company_workspace_root(
    company_workspace_root: Path | None,
) -> Path:
    """解析 COMPANY_WORKSPACE_ROOT；相對路徑以 framework repo 根為準。"""
    base = framework_repo_root()
    if company_workspace_root is None:
        return (base / DEFAULT_WORKSPACE_DIR_NAME).resolve()
    raw = company_workspace_root.expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (base / raw).resolve()


def project_dir(workspace_root: Path, project_id: str) -> Path:
    return workspace_root / PROJECTS_DIR_NAME / project_id
