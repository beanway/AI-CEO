"""任務分配者 scripted runner（假 AI 序列）。"""

import yaml

from ai_company.modules.worker_runner import core as worker_runner
from ai_company.modules.worker_runner.core import (
    BackendTaskContract,
    PlannedToolCall,
    ScriptedAgentTurn,
)


def _fixture_yaml(name: str) -> str:
    return (worker_runner.worker_default_fixtures_dir() / name).read_text(encoding="utf-8")


def _scheduler_scripted_turns() -> list[ScriptedAgentTurn]:
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
                    "read_skill",
                    {"skill_file": "01_analyze_and_plan.md"},
                ),
                PlannedToolCall(
                    "read_file",
                    {"path": "workers.yaml"},
                ),
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
                    {
                        "status": "success",
                        "summary": "規劃 1 個 backend 任務",
                    },
                ),
            ],
        ),
    ]


def test_scripted_scheduler_writes_task_queue(tmp_workspace):
    worker_runner.seed_scheduler_backend_demo_project(tmp_workspace, "sch1")
    result = worker_runner.run_scheduler_worker_scripted(
        tmp_workspace, "sch1", "scheduler", _scheduler_scripted_turns()
    )
    assert result.success is True
    assert result.tasks_planned == 1
    assert result.plan_id == "demo-plan-2026"
    tq = tmp_workspace / "projects" / "sch1" / "pm" / "task_queue.yaml"
    assert tq.is_file()
    backend_task = (
        tmp_workspace / "projects" / "sch1" / "pm" / "backend_current_task.yaml"
    )
    assert backend_task.is_file()
    last = worker_runner.load_scheduler_last_run(tmp_workspace, "sch1", "scheduler")
    assert last is not None and last.status == "success"
