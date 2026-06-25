"""task_scheduler 路徑政策單元測試。"""

import pytest

from ai_company.modules.file_store import core as file_store
from ai_company.modules.sandbox_runner.core import (
    ToolPolicyError,
    validate_scheduler_relative_path,
)
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.schemas.documents import WorkerEntry, WorkersFile


def test_scheduler_can_write_pm(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    pid = "sch_pol"
    root = project_folders.project_dir(tmp_workspace, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(
        workers=[WorkerEntry(id="scheduler", kind="task_scheduler")]
    )
    file_store.save_workers(tmp_workspace, pid, workers)
    project_folders.ensure_worker_directories(root, workers.workers)
    path = validate_scheduler_relative_path(
        tmp_workspace, pid, "scheduler", "pm/task_queue.yaml", for_write=True
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("plan_id: x\ntasks: []\n", encoding="utf-8")


def test_scheduler_cannot_write_backend_worker_dir(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    pid = "sch_pol2"
    root = project_folders.project_dir(tmp_workspace, pid)
    project_folders.ensure_project_tree(root)
    with pytest.raises(ToolPolicyError):
        validate_scheduler_relative_path(
            tmp_workspace,
            pid,
            "scheduler",
            "workers/backend/calc.py",
            for_write=True,
        )


def test_scheduler_can_read_workers_yaml(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    pid = "sch_pol3"
    root = project_folders.project_dir(tmp_workspace, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(
        workers=[
            WorkerEntry(id="scheduler", kind="task_scheduler"),
            WorkerEntry(id="backend", kind="backend"),
        ]
    )
    file_store.save_workers(tmp_workspace, pid, workers)
    path = validate_scheduler_relative_path(
        tmp_workspace, pid, "scheduler", "workers.yaml", for_write=False
    )
    assert path.name == "workers.yaml"
