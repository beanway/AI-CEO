"""worker_host backend 路徑。"""

from ai_company.modules.worker_host import core as worker_host
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.modules.worker_runner.core import PlannedToolCall, ScriptedAgentTurn

CALC_PY = '''"""Calc."""
def add(a, b):
    return a + b
'''

TEST_CALC = '''from calc import add

def test_add():
    assert add(2, 3) == 5
'''


def test_host_backend_scripted_matches_runner(tmp_workspace):
    worker_runner.seed_backend_worker_project(tmp_workspace, "host1")
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
                        "summary": "ok",
                        "test_command": "python3 -m pytest workers/backend/test_calc.py -q",
                        "test_exit_code": 0,
                    },
                ),
            ],
        ),
    ]
    result = worker_host.run_backend_scripted(tmp_workspace, "host1", "backend", turns)
    assert result.success
    last = worker_runner.load_last_run(tmp_workspace, "host1", "backend")
    assert last is not None and last.status == "success"


def test_host_execution_step_writes_last_run(tmp_workspace):
    worker_runner.seed_backend_worker_project(tmp_workspace, "host2")
    result = worker_host.run_backend_execution_step(tmp_workspace, "host2", "backend")
    assert result.success
    assert "last_run" in result.last_run_path
