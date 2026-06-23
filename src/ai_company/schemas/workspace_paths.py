"""工作區路徑常數與純函式（模組共用，避免重複 project_dir）。"""

from __future__ import annotations

from pathlib import Path

PROJECTS_DIR_NAME = "projects"


def project_dir(workspace_root: Path, project_id: str) -> Path:
    return workspace_root / PROJECTS_DIR_NAME / project_id
