from __future__ import annotations

import secrets
import shutil
from pathlib import Path

from ai_company.models.company import ProjectRecord, ProjectsFile, UserMode, UserPref
from ai_company.modules.format_messages.core import format_projects_message
from ai_company.services.project_paths import ensure_project_tree, project_dir
from ai_company.store.company_store import CompanyStore

DEFAULT_PROJECT_ID = "default"

__all__ = ["CompanyService", "format_projects_message", "DEFAULT_PROJECT_ID"]


class CompanyService:
    def __init__(self, workspace_root: Path, store: CompanyStore) -> None:
        self.workspace_root = workspace_root
        self.store = store

    def bootstrap_default_project_if_needed(self) -> None:
        pf = self.store.load_projects()
        legacy = project_dir(self.workspace_root, DEFAULT_PROJECT_ID)
        if legacy.is_dir() and not any(p.id == DEFAULT_PROJECT_ID for p in pf.projects):
            pf.projects.append(ProjectRecord(id=DEFAULT_PROJECT_ID, name="Default"))
            if pf.active_project_id is None:
                pf.active_project_id = DEFAULT_PROJECT_ID
            self.store.save_projects(pf)

    def list_projects(self) -> ProjectsFile:
        self.bootstrap_default_project_if_needed()
        return self.store.load_projects()

    def set_active_project(self, project_id: str) -> ProjectRecord:
        self.bootstrap_default_project_if_needed()
        pf = self.store.load_projects()
        rec = next((p for p in pf.projects if p.id == project_id), None)
        if rec is None:
            known = ", ".join(sorted(p.id for p in pf.projects)) or "（無）"
            raise ValueError(f"找不到專案 id={project_id!r}。可用：{known}")
        pf.active_project_id = project_id
        self.store.save_projects(pf)
        return rec

    def get_active_project(self) -> ProjectRecord | None:
        pf = self.list_projects()
        if pf.active_project_id is None:
            return None
        return next((p for p in pf.projects if p.id == pf.active_project_id), None)

    def create_project(self, name: str, *, initial_requirements: str | None = None) -> ProjectRecord:
        project_id = secrets.token_hex(4)
        root = project_dir(self.workspace_root, project_id)
        try:
            ensure_project_tree(root)
            if initial_requirements is not None:
                (root / "shared" / "requirements.md").write_text(
                    initial_requirements, encoding="utf-8"
                )
            pf = self.store.load_projects()
            rec = ProjectRecord(id=project_id, name=name)
            pf.projects.append(rec)
            if pf.active_project_id is None:
                pf.active_project_id = project_id
            self.store.save_projects(pf)
            return rec
        except Exception:
            shutil.rmtree(root, ignore_errors=True)
            raise

    def set_user_mode(self, tg_user_id: int, mode: UserMode) -> None:
        prefs = self.store.load_user_prefs()
        prefs.users[str(tg_user_id)] = UserPref(mode=mode)
        self.store.save_user_prefs(prefs)

    def get_user_mode(self, tg_user_id: int) -> UserMode:
        prefs = self.store.load_user_prefs()
        pref = prefs.users.get(str(tg_user_id))
        if pref is None:
            return UserMode.CEO
        return pref.mode
