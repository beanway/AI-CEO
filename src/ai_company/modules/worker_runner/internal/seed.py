"""從 worker_default 種子建立 fixture 專案。"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner.internal.contracts import BackendTaskContract
from ai_company.schemas.documents import WorkerEntry, WorkersFile
from ai_company.schemas.workspace_paths import framework_repo_root, project_dir


def worker_default_backend_dir() -> Path:
    return framework_repo_root() / "worker_default" / "backend"


def worker_default_fixtures_dir() -> Path:
    return framework_repo_root() / "worker_default" / "fixtures"


def seed_backend_worker_project(
    workspace_root: Path,
    project_id: str,
    *,
    worker_id: str = "backend",
    task: BackendTaskContract | None = None,
) -> Path:
    """建立專案樹、workers.yaml、複製 backend 種子、寫入任務契約。"""
    file_store.ensure_company_dirs(workspace_root)
    root = project_folders.project_dir(workspace_root, project_id)
    project_folders.ensure_project_tree(root)

    workers = WorkersFile(workers=[WorkerEntry(id=worker_id, kind="backend")])
    file_store.save_workers(workspace_root, project_id, workers)
    project_folders.ensure_worker_directories(root, workers.workers)

    dest_worker = root / "workers" / worker_id
    seed = worker_default_backend_dir()
    for name in ("SKILL.md", "role_skills.yaml"):
        src = seed / name
        if src.is_file():
            shutil.copy2(src, dest_worker / name)
    skills_src = seed / "skills"
    skills_dest = dest_worker / "skills"
    if skills_src.is_dir():
        if skills_dest.exists():
            shutil.rmtree(skills_dest)
        shutil.copytree(skills_src, skills_dest)

    shared = root / "shared"
    shared.mkdir(parents=True, exist_ok=True)
    req_snippet = worker_default_fixtures_dir() / "shared_requirements_snippet.md"
    req_path = shared / "requirements.md"
    if req_snippet.is_file():
        shutil.copy2(req_snippet, req_path)
    elif not req_path.is_file():
        req_path.write_text("# Requirements\n", encoding="utf-8")

    pm = root / "pm"
    pm.mkdir(parents=True, exist_ok=True)
    if task is None:
        raw = yaml.safe_load(
            (worker_default_fixtures_dir() / "backend_demo_task.yaml").read_text(encoding="utf-8")
        )
        task = BackendTaskContract.model_validate(raw)
    task_path = pm / "backend_current_task.yaml"
    task_path.write_text(
        yaml.safe_dump(task.model_dump(), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return project_dir(workspace_root, project_id)
