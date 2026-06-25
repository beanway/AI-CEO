"""worker_default 種子複製（單元）。"""

from pathlib import Path

import pytest

from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner import core as worker_runner


def test_default_worker_entry_backend():
    entry = worker_runner.default_worker_entry_for_template("backend")
    assert entry.id == "backend"
    assert entry.kind == "backend"


def test_default_worker_entry_scheduler():
    entry = worker_runner.default_worker_entry_for_template("scheduler")
    assert entry.id == "scheduler"
    assert entry.kind == "task_scheduler"


def test_copy_worker_default_scheduler_files(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    dest = worker_runner.copy_worker_default_into_worker_dir(root, "scheduler")
    assert dest == root / "workers" / "scheduler"
    assert (dest / "SKILL.md").is_file()
    assert (dest / "skills" / "01_analyze_and_plan.md").is_file()


def test_copy_worker_default_backend_files(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    dest = worker_runner.copy_worker_default_into_worker_dir(root, "backend")
    assert dest.is_dir()
    assert (dest / "SKILL.md").is_file()
    assert (dest / "worker_manifest.yaml").is_file()
    assert (dest / "package" / "backend_worker" / "run.py").is_file()
    assert (dest / "skills" / "01_plan_implement_test.md").is_file()


def test_unknown_template_raises():
    with pytest.raises(ValueError):
        worker_runner.default_worker_entry_for_template("unknown")
