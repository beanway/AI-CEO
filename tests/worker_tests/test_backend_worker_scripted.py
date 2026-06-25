"""離線整合：在 worker_tests 沙盒跑 scripted demo，產物供人工檢視。"""

from pathlib import Path

from ai_company.modules.worker_runner import core as worker_runner
from ai_company.modules.worker_runner.core import PlannedToolCall, ScriptedAgentTurn

SANDBOX_ROOT = Path(__file__).resolve().parent / "_sandbox"
PROJECT_ID = "worker_scripted_demo"
WORKER_ID = "backend"

CALC_PY = '''"""Calc module."""
def add(a, b):
    return a + b
'''

TEST_CALC = '''from calc import add

def test_add():
    assert add(2, 3) == 5
'''


def test_backend_worker_scripted_produces_reviewable_artifacts():
    root = SANDBOX_ROOT / "company_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(SANDBOX_ROOT)
    root.mkdir(parents=True)
    worker_runner.seed_backend_worker_project(root, PROJECT_ID, worker_id=WORKER_ID)
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
                        "summary": "scripted demo 完成",
                        "test_command": "python3 -m pytest workers/backend/test_calc.py -q",
                        "test_exit_code": 0,
                    },
                ),
            ],
        ),
    ]
    result = worker_runner.run_backend_worker_scripted(
        root, PROJECT_ID, WORKER_ID, turns
    )
    assert result.success
    assert (
        root / "projects" / PROJECT_ID / "workers" / WORKER_ID / "calc.py"
    ).is_file()
