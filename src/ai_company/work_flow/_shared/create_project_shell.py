"""CEO 建專案殼編排（目錄、索引、PM session）；失敗回滾。"""

from __future__ import annotations

import secrets
import shutil

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.schemas.documents import ProjectRecord


def create_project_shell(
    deps: AppDeps,
    name: str,
    *,
    initial_requirements: str | None = None,
) -> ProjectRecord:
    workspace_root = deps.workspace_root
    project_id = secrets.token_hex(4)
    root = project_folders.project_dir(workspace_root, project_id)
    session_written = False
    prev_active: str | None = None
    projects_saved = False
    rec = ProjectRecord(id=project_id, name=name)
    try:
        project_folders.ensure_project_tree(root)
        if initial_requirements is not None:
            (root / "shared" / "requirements.md").write_text(
                initial_requirements, encoding="utf-8"
            )
        prev_active = file_store.add_project_record(workspace_root, rec)
        projects_saved = True
        file_store.init_pm_session(workspace_root, project_id)
        session_written = True
        return rec
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        if session_written:
            file_store.delete_pm_session(workspace_root, project_id)
        if projects_saved:
            file_store.revert_add_project(workspace_root, project_id, prev_active)
        raise
