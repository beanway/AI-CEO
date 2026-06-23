"""PM flow 共用：解析 active 專案 id。"""

from __future__ import annotations

from pathlib import Path

from ai_company.modules.file_store import core as file_store


def require_active_project_id(workspace_root: Path, project_id: str | None) -> str:
    try:
        return file_store.resolve_project_id(workspace_root, project_id)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
