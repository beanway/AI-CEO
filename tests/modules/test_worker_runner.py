import pytest

from ai_company.modules.file_store import core as file_store
from ai_company.modules.sandbox_runner.core import ToolPolicyError, run_argv_in_worker_cwd
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.modules.worker_runner.core import PlannedToolCall, ScriptedAgentTurn
from ai_company.schemas.documents import WorkerEntry, WorkersFile

CALC_PY = '''"""Calc module."""
def add(a, b):
    return a + b
'''

TEST_CALC = '''from calc import add

def test_add():
    assert add(2, 3) == 5
'''


def test_seed_copies_skills(tmp_workspace):
    worker_runner.seed_backend_worker_project(tmp_workspace, "wt1")
    skill = (
        tmp_workspace
        / "projects"
        / "wt1"
        / "workers"
        / "backend"
        / "skills"
        / "01_plan_implement_test.md"
    )
    assert skill.is_file()


def test_run_argv_rejects_pip(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    pid = "p_pip"
    root = project_folders.project_dir(tmp_workspace, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(workers=[WorkerEntry(id="backend", kind="backend")])
    file_store.save_workers(tmp_workspace, pid, workers)
    project_folders.ensure_worker_directories(root, workers.workers)
    with pytest.raises(ToolPolicyError):
        run_argv_in_worker_cwd(tmp_workspace, pid, "backend", ["pip", "install", "x"])


def test_scripted_backend_worker_completes_demo_task(tmp_workspace):
    worker_runner.seed_backend_worker_project(tmp_workspace, "wt2")
    turns = [
        ScriptedAgentTurn(
            tool_calls=[
                PlannedToolCall(
                    "write_file",
                    {"path": "workers/backend/calc.py", "content": CALC_PY},
                ),
                PlannedToolCall(
                    "write_file",
                    {"path": "workers/backend/test_calc.py", "content": TEST_CALC},
                ),
                PlannedToolCall(
                    "run_terminal",
                    {
                        "argv": [
                            "python3",
                            "-m",
                            "pytest",
                            "workers/backend/test_calc.py",
                            "-q",
                        ],
                    },
                ),
                PlannedToolCall(
                    "complete_task",
                    {
                        "status": "success",
                        "summary": "add() 與 pytest 完成",
                        "test_command": "python3 -m pytest workers/backend/test_calc.py -q",
                        "test_exit_code": 0,
                    },
                ),
            ],
        ),
    ]
    result = worker_runner.run_backend_worker_scripted(
        tmp_workspace, "wt2", "backend", turns
    )
    assert result.success is True
    assert result.task_id == "demo-add-2026"
    last = worker_runner.load_last_run(tmp_workspace, "wt2", "backend")
    assert last is not None
    assert last.status == "success"
    calc = (
        tmp_workspace
        / "projects"
        / "wt2"
        / "workers"
        / "backend"
        / "calc.py"
    )
    assert calc.is_file()
