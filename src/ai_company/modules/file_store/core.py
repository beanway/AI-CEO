"""讀寫 company_workspace 內 _company 設定檔（JSON/YAML）。"""

from __future__ import annotations

import secrets
import shutil
from pathlib import Path

from ai_company.modules.file_store.internal.store import FileStore
from ai_company.modules.setup_project_folders.core import ensure_project_tree, project_dir
from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    ProjectRecord,
    ProjectsFile,
    SessionRecord,
    UserMode,
    UserPref,
    UserPrefsFile,
)

DEFAULT_PROJECT_ID = "default"


def _store(workspace_root: Path) -> FileStore:
    return FileStore(workspace_root)


def ensure_company_dirs(workspace_root: Path) -> None:
    _store(workspace_root).ensure_company_dirs()


def ensure_company_index_files(workspace_root: Path) -> None:
    _store(workspace_root).ensure_company_index_files()


def load_projects(workspace_root: Path) -> ProjectsFile:
    bootstrap_default_project_if_needed(workspace_root)
    return _store(workspace_root).load_projects()


def save_projects(workspace_root: Path, data: ProjectsFile) -> None:
    _store(workspace_root).save_projects(data)


def load_global_skills(workspace_root: Path) -> GlobalSkillsFile:
    return _store(workspace_root).load_global_skills()


def load_global_config(workspace_root: Path) -> GlobalConfigFile:
    return _store(workspace_root).load_global_config()


def save_global_skills(workspace_root: Path, data: GlobalSkillsFile) -> None:
    _store(workspace_root).save_global_skills(data)


def save_global_config(workspace_root: Path, data: GlobalConfigFile) -> None:
    _store(workspace_root).save_global_config(data)


def bootstrap_default_project_if_needed(workspace_root: Path) -> None:
    store = _store(workspace_root)
    pf = store.load_projects()
    legacy = project_dir(workspace_root, DEFAULT_PROJECT_ID)
    if legacy.is_dir() and not any(p.id == DEFAULT_PROJECT_ID for p in pf.projects):
        pf.projects.append(ProjectRecord(id=DEFAULT_PROJECT_ID, name="Default"))
        if pf.active_project_id is None:
            pf.active_project_id = DEFAULT_PROJECT_ID
        store.save_projects(pf)


def set_active_project(workspace_root: Path, project_id: str) -> ProjectRecord:
    bootstrap_default_project_if_needed(workspace_root)
    store = _store(workspace_root)
    pf = store.load_projects()
    rec = next((p for p in pf.projects if p.id == project_id), None)
    if rec is None:
        known = ", ".join(sorted(p.id for p in pf.projects)) or "（無）"
        raise ValueError(f"找不到專案 id={project_id!r}。可用：{known}")
    pf.active_project_id = project_id
    store.save_projects(pf)
    return rec


def get_active_project(workspace_root: Path) -> ProjectRecord | None:
    pf = load_projects(workspace_root)
    if pf.active_project_id is None:
        return None
    return next((p for p in pf.projects if p.id == pf.active_project_id), None)


def create_project(
    workspace_root: Path,
    name: str,
    *,
    initial_requirements: str | None = None,
) -> ProjectRecord:
    project_id = secrets.token_hex(4)
    root = project_dir(workspace_root, project_id)
    store = _store(workspace_root)
    session_path: Path | None = None
    prev_active: str | None = None
    projects_saved = False
    try:
        ensure_project_tree(root)
        if initial_requirements is not None:
            (root / "shared" / "requirements.md").write_text(
                initial_requirements, encoding="utf-8"
            )
        pf = store.load_projects()
        prev_active = pf.active_project_id
        rec = ProjectRecord(id=project_id, name=name)
        pf.projects.append(rec)
        if pf.active_project_id is None:
            pf.active_project_id = project_id
        store.save_projects(pf)
        projects_saved = True
        session_path = store.session_path(project_id)
        store.save_session(
            session_path,
            SessionRecord(gemini_chat_name="", project_id=project_id),
        )
        return rec
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        if session_path is not None and session_path.exists():
            session_path.unlink(missing_ok=True)
        if projects_saved:
            pf = store.load_projects()
            pf.projects = [p for p in pf.projects if p.id != project_id]
            if pf.active_project_id == project_id:
                remaining = pf.projects
                pf.active_project_id = (
                    prev_active
                    if prev_active and any(p.id == prev_active for p in remaining)
                    else (remaining[0].id if remaining else None)
                )
            store.save_projects(pf)
        raise


def set_user_mode(workspace_root: Path, tg_user_id: int, mode: UserMode) -> None:
    store = _store(workspace_root)
    prefs = store.load_user_prefs()
    prefs.users[str(tg_user_id)] = UserPref(mode=mode)
    store.save_user_prefs(prefs)


def get_user_mode(workspace_root: Path, tg_user_id: int) -> UserMode:
    pref = _store(workspace_root).load_user_prefs().users.get(str(tg_user_id))
    if pref is None:
        return UserMode.CEO
    return pref.mode
