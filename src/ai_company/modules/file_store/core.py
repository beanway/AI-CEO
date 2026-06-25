"""讀寫 company_workspace 內 _company 設定檔（JSON/YAML）。"""

from __future__ import annotations

from pathlib import Path

import json
import secrets

import yaml

from ai_company.schemas.workspace_paths import project_dir
from ai_company.modules.file_store.internal.store import COMPANY_GITIGNORE_TEXT, FileStore
from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    PendingApprovalRecord,
    PendingApprovalsFile,
    PendingExecutionFailureRecord,
    PendingExecutionFailuresFile,
    ProjectHarnessStateFile,
    ProjectLifecycle,
    ProjectRecord,
    ProjectSkillsFile,
    ProjectsFile,
    SessionRecord,
    UserMode,
    UserPref,
    UserPrefsFile,
    WorkersFile,
    ApprovalStatus,
)

DEFAULT_PROJECT_ID = "default"


def _store(workspace_root: Path) -> FileStore:
    return FileStore(workspace_root)


def ensure_company_dirs(workspace_root: Path) -> None:
    _store(workspace_root).ensure_company_dirs()


def ensure_company_index_files(workspace_root: Path) -> None:
    from ai_company.modules.settings.core import default_global_config

    _store(workspace_root).ensure_company_index_files(
        initial_global_config=default_global_config(),
    )


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


def add_project_record(workspace_root: Path, record: ProjectRecord) -> str | None:
    """新增專案索引；若尚無 active 則設為此專案。回傳先前的 active_project_id。"""
    store = _store(workspace_root)
    pf = store.load_projects()
    prev_active = pf.active_project_id
    pf.projects.append(record)
    if pf.active_project_id is None:
        pf.active_project_id = record.id
    store.save_projects(pf)
    return prev_active


def revert_add_project(
    workspace_root: Path, project_id: str, prev_active: str | None
) -> None:
    store = _store(workspace_root)
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


def init_pm_session(workspace_root: Path, project_id: str) -> None:
    save_pm_session(
        workspace_root,
        project_id,
        SessionRecord(gemini_chat_name="", project_id=project_id),
    )


def delete_pm_session(workspace_root: Path, project_id: str) -> None:
    path = _store(workspace_root).session_path(project_id)
    path.unlink(missing_ok=True)


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


def load_ceo_session(workspace_root: Path) -> SessionRecord | None:
    store = _store(workspace_root)
    return store.load_session(store.session_path("ceo"))


def save_ceo_session(workspace_root: Path, record: SessionRecord) -> None:
    store = _store(workspace_root)
    store.save_session(store.session_path("ceo"), record)


def load_pm_session(workspace_root: Path, project_id: str) -> SessionRecord | None:
    store = _store(workspace_root)
    return store.load_session(store.session_path(project_id))


def save_pm_session(workspace_root: Path, project_id: str, record: SessionRecord) -> None:
    store = _store(workspace_root)
    store.save_session(store.session_path(project_id), record)


def _project_root(workspace_root: Path, project_id: str) -> Path:
    return project_dir(workspace_root, project_id)


def load_workers(workspace_root: Path, project_id: str) -> WorkersFile:
    path = _project_root(workspace_root, project_id) / "workers.yaml"
    if not path.is_file():
        return WorkersFile()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return WorkersFile()
    return WorkersFile.model_validate(raw)


def save_workers(workspace_root: Path, project_id: str, data: WorkersFile) -> None:
    root = _project_root(workspace_root, project_id)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "workers.yaml"
    body = yaml.safe_dump(
        data.model_dump(mode="json"),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    store = _store(workspace_root)
    store.write_text_file(path, body)


def load_project_skills(workspace_root: Path, project_id: str) -> ProjectSkillsFile:
    path = _project_root(workspace_root, project_id) / "project_skills.yaml"
    if not path.is_file():
        return ProjectSkillsFile()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return ProjectSkillsFile()
    return ProjectSkillsFile.model_validate(raw)


def save_project_skills(
    workspace_root: Path, project_id: str, data: ProjectSkillsFile
) -> None:
    root = _project_root(workspace_root, project_id)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "project_skills.yaml"
    body = yaml.safe_dump(
        data.model_dump(mode="json"),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    store = _store(workspace_root)
    store.write_text_file(path, body)


def resolve_project_id(workspace_root: Path, project_id: str | None) -> str:
    if project_id is not None and project_id.strip():
        return project_id.strip()
    active = get_active_project(workspace_root)
    if active is None:
        raise ValueError("尚無 active 專案，請先 /switch 或 /newproject。")
    return active.id


def load_pending_approvals(workspace_root: Path) -> PendingApprovalsFile:
    return _store(workspace_root).load_pending_approvals()


def save_pending_approvals(workspace_root: Path, data: PendingApprovalsFile) -> None:
    _store(workspace_root).save_pending_approvals(data)


def create_pending_approval(
    workspace_root: Path,
    *,
    record: PendingApprovalRecord,
) -> PendingApprovalRecord:
    store = _store(workspace_root)
    data = store.load_pending_approvals()
    approval_id = secrets.token_hex(4)
    while approval_id in data.items:
        approval_id = secrets.token_hex(4)
    stored = record.model_copy(update={"id": approval_id})
    data.items[approval_id] = stored
    store.save_pending_approvals(data)
    return stored


def get_pending_approval(
    workspace_root: Path, approval_id: str
) -> PendingApprovalRecord | None:
    return load_pending_approvals(workspace_root).items.get(approval_id)


def update_pending_approval(
    workspace_root: Path, record: PendingApprovalRecord
) -> None:
    data = load_pending_approvals(workspace_root)
    data.items[record.id] = record
    save_pending_approvals(workspace_root, data)


def _harness_state_path(workspace_root: Path, project_id: str) -> Path:
    return project_dir(workspace_root, project_id) / "pm" / "harness_state.json"


def load_project_harness_state(
    workspace_root: Path, project_id: str
) -> ProjectHarnessStateFile:
    path = _harness_state_path(workspace_root, project_id)
    if not path.is_file():
        return ProjectHarnessStateFile()
    return ProjectHarnessStateFile.model_validate_json(path.read_text(encoding="utf-8"))


def save_project_harness_state(
    workspace_root: Path, project_id: str, state: ProjectHarnessStateFile
) -> None:
    path = _harness_state_path(workspace_root, project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)


def append_scheduler_decision(
    workspace_root: Path,
    project_id: str,
    *,
    event: str,
    worker_id: str | None = None,
    detail: str = "",
) -> None:
    log_path = project_dir(workspace_root, project_id) / "pm" / "scheduler_decisions.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "event": event,
        "worker_id": worker_id,
        "detail": detail,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def set_project_lifecycle_done(workspace_root: Path, project_id: str) -> None:
    pf = load_projects(workspace_root)
    updated: list[ProjectRecord] = []
    for rec in pf.projects:
        if rec.id == project_id:
            updated.append(rec.model_copy(update={"status": ProjectLifecycle.PROJECT_DONE.value}))
        else:
            updated.append(rec)
    save_projects(workspace_root, pf.model_copy(update={"projects": updated}))


def load_pending_execution_failures(workspace_root: Path) -> PendingExecutionFailuresFile:
    return _store(workspace_root).load_pending_execution_failures()


def save_pending_execution_failures(
    workspace_root: Path, data: PendingExecutionFailuresFile
) -> None:
    _store(workspace_root).save_pending_execution_failures(data)


def create_pending_execution_failure(
    workspace_root: Path,
    *,
    record: PendingExecutionFailureRecord,
) -> PendingExecutionFailureRecord:
    store = _store(workspace_root)
    data = store.load_pending_execution_failures()
    failure_id = secrets.token_hex(4)
    while failure_id in data.items:
        failure_id = secrets.token_hex(4)
    stored = record.model_copy(update={"id": failure_id})
    data.items[failure_id] = stored
    store.save_pending_execution_failures(data)
    return stored


def get_pending_execution_failure(
    workspace_root: Path, failure_id: str
) -> PendingExecutionFailureRecord | None:
    return load_pending_execution_failures(workspace_root).items.get(failure_id)


def update_pending_execution_failure(
    workspace_root: Path, record: PendingExecutionFailureRecord
) -> None:
    data = load_pending_execution_failures(workspace_root)
    data.items[record.id] = record
    save_pending_execution_failures(workspace_root, data)


def pending_execution_failure_for_project(
    workspace_root: Path, project_id: str
) -> PendingExecutionFailureRecord | None:
    for item in load_pending_execution_failures(workspace_root).items.values():
        if item.project_id == project_id and item.status == ApprovalStatus.PENDING:
            return item
    return None
