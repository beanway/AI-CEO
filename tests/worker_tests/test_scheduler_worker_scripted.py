"""離線整合：scheduler（scripted）規劃後 backend（scripted）執行。"""

from pathlib import Path

import yaml

from ai_company.modules.worker_runner import core as worker_runner
from ai_company.modules.worker_runner.core import (
    BackendTaskContract,
    PlannedToolCall,
    ScriptedAgentTurn,
)

SANDBOX_ROOT = Path(__file__).resolve().parent / "_sandbox"
PROJECT_ID = "scheduler_backend_scripted"
SCHEDULER_ID = "scheduler"
BACKEND_ID = "backend"

CALC_PY = '''"""Calc module."""
def add(a, b):
    return a + b
'''

TEST_CALC = '''from calc import add

def test_add():
    assert add(2, 3) == 5
'''


def _fixture_yaml(name: str) -> str:
    return (worker_runner.worker_default_fixtures_dir() / name).read_text(encoding="utf-8")


def _scheduler_turns() -> list[ScriptedAgentTurn]:
    queue_yaml = _fixture_yaml("scheduler_demo_task_queue.yaml")
    plan = yaml.safe_load(queue_yaml)
    first = plan["tasks"][0]
    backend_task = BackendTaskContract(
        task_id=first["task_id"],
        goal=first["goal"],
        acceptance_criteria=first.get("acceptance_criteria", []),
        allowed_paths=["workers/backend/"],
        context_refs=["shared/requirements.md"],
    )
    backend_yaml = yaml.safe_dump(
        backend_task.model_dump(), allow_unicode=True, sort_keys=False
    )
    return [
        ScriptedAgentTurn(
            tool_calls=[
                PlannedToolCall(
                    "write_file",
                    {"path": "pm/task_queue.yaml", "content": queue_yaml},
                ),
                PlannedToolCall(
                    "write_file",
                    {
                        "path": "pm/backend_current_task.yaml",
                        "content": backend_yaml,
                    },
                ),
                PlannedToolCall(
                    "complete_task",
                    {"status": "success", "summary": "demo plan"},
                ),
            ],
        ),
    ]


def _backend_turns() -> list[ScriptedAgentTurn]:
    return [
        ScriptedAgentTurn(
            tool_calls=[
                PlannedToolCall(
                    "write_file",
                    {"path": "workers/backend/calc.py", "content": CALC_PY},
                ),
                PlannedToolCall(
                    "write_file",
                    {
                        "path": "workers/backend/test_calc.py",
                        "content": TEST_CALC,
                    },
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
                        "summary": "backend after scheduler",
                        "test_command": "python3 -m pytest workers/backend/test_calc.py -q",
                        "test_exit_code": 0,
                    },
                ),
            ],
        ),
    ]


def test_scheduler_then_backend_scripted_pipeline():
    root = SANDBOX_ROOT / "company_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(SANDBOX_ROOT)
    root.mkdir(parents=True)
    worker_runner.seed_scheduler_backend_demo_project(root, PROJECT_ID)

    sched = worker_runner.run_scheduler_worker_scripted(
        root, PROJECT_ID, SCHEDULER_ID, _scheduler_turns()
    )
    assert sched.success, sched.summary

    back = worker_runner.run_backend_worker_scripted(
        root, PROJECT_ID, BACKEND_ID, _backend_turns()
    )
    assert back.success, back.summary
    assert (
        root / "projects" / PROJECT_ID / "workers" / BACKEND_ID / "calc.py"
    ).is_file()
