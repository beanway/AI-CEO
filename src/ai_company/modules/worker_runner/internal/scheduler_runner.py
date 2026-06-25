"""任務分配者 Worker 執行（scripted / 未來 Gemini）。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

from ai_company.modules.sandbox_runner.core import ToolPolicyError
from ai_company.modules.worker_runner.internal.contracts import (
    SchedulerIntakeContract,
    SchedulerLastRun,
    TaskQueuePlan,
)
from ai_company.modules.worker_runner.internal.scheduler_harness_tools import (
    SchedulerHarnessToolContext,
    dispatch_scheduler_tool,
)
from ai_company.modules.worker_runner.internal.scripted_agent import (
    ScriptedAgentDriver,
    ScriptedAgentTurn,
)
from ai_company.schemas.workspace_paths import project_dir

DEFAULT_MAX_TURNS = 25

SCHEDULER_SYSTEM_PREFIX = """你是專案沙盒內的任務分配者（task_scheduler Worker）。
工作目錄為專案根。收到 intake 後：
1. 用 list_skills / read_skill 閱讀 workers/<worker_id>/skills/ 劇本。
2. 用 read_file 讀 workers.yaml、shared/requirements.md、pm/scheduler_intake.yaml。
3. 用 write_file 寫入 pm/task_queue.yaml 與第一個執行者的 pm/*_current_task.yaml。
4. 規劃完成後呼叫 complete_task（status=success）。
禁止修改執行者程式目錄、禁止 run_terminal。
"""


@dataclass(frozen=True)
class SchedulerWorkerRunResult:
    success: bool
    task_id: str
    summary: str
    last_run_path: str
    turns_used: int
    plan_id: str | None = None
    tasks_planned: int = 0
    error: str | None = None


class _AgentDriver(Protocol):
    def start(self, system_instruction: str, user_task: str) -> None: ...

    def next_turn(self) -> Any: ...

    def submit_tool_results(self, results: list[tuple[str, Any]]) -> None: ...


def _load_intake(workspace_root: Path, project_id: str) -> SchedulerIntakeContract:
    path = project_dir(workspace_root, project_id) / "pm" / "scheduler_intake.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"缺少 intake：{path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return SchedulerIntakeContract.model_validate(raw)


def _build_user_message(intake: SchedulerIntakeContract, worker_id: str) -> str:
    lines = [
        f"task_id: {intake.task_id}",
        f"worker_id: {worker_id}",
        "",
        "user_goal:",
        intake.user_goal.strip(),
    ]
    if intake.context_refs:
        lines.append("")
        lines.append("context_refs:")
        lines.extend(f"- {r}" for r in intake.context_refs)
    lines.append("")
    lines.append("請開始：先 list_skills，再依劇本分析並寫入 task_queue。")
    return "\n".join(lines)


def _load_task_queue(workspace_root: Path, project_id: str) -> TaskQueuePlan:
    path = project_dir(workspace_root, project_id) / "pm" / "task_queue.yaml"
    if not path.is_file():
        raise FileNotFoundError("缺少 pm/task_queue.yaml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return TaskQueuePlan.model_validate(raw)


def _write_last_run(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    payload: SchedulerLastRun,
) -> Path:
    path = (
        project_dir(workspace_root, project_id) / "workers" / worker_id / "last_run.json"
    )
    path.write_text(
        json.dumps(payload.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _handle_complete_task(
    ctx: SchedulerHarnessToolContext,
    intake: SchedulerIntakeContract,
    args: dict,
) -> SchedulerWorkerRunResult:
    status = str(args.get("status", "failed"))
    summary = str(args.get("summary", ""))
    notes = str(args.get("notes_for_reviewer", ""))
    plan_id: str | None = None
    tasks_planned = 0

    if status == "success":
        try:
            plan = _load_task_queue(ctx.workspace_root, ctx.project_id)
            plan_id = plan.plan_id
            tasks_planned = len(plan.tasks)
            if tasks_planned < 1:
                status = "failed"
                summary = "task_queue.yaml 無任務"
        except Exception as exc:
            status = "failed"
            summary = f"無法驗證 task_queue：{exc}"

    last = SchedulerLastRun(
        task_id=intake.task_id,
        status=status,
        files_changed=list(ctx.files_changed),
        summary=summary,
        notes_for_reviewer=notes,
        plan_id=plan_id,
        tasks_planned=tasks_planned,
    )
    path = _write_last_run(ctx.workspace_root, ctx.project_id, ctx.worker_id, last)
    rel = str(path.relative_to(project_dir(ctx.workspace_root, ctx.project_id)))
    ok = status == "success"
    return SchedulerWorkerRunResult(
        success=ok,
        task_id=intake.task_id,
        summary=summary,
        last_run_path=rel,
        turns_used=0,
        plan_id=plan_id,
        tasks_planned=tasks_planned,
        error=None if ok else summary,
    )


def _run_agent_loop(
    *,
    driver: _AgentDriver,
    system_instruction: str,
    user_task: str,
    ctx: SchedulerHarnessToolContext,
    intake: SchedulerIntakeContract,
    max_turns: int,
) -> SchedulerWorkerRunResult:
    driver.start(system_instruction, user_task)
    turns = 0
    last_error: str | None = None

    while turns < max_turns:
        turns += 1
        turn = driver.next_turn()
        if turn is None:
            last_error = "Agent 無後續步驟"
            break
        tool_calls: list[tuple[str, dict]] = []

        if isinstance(turn, ScriptedAgentTurn):
            if turn.text and not turn.tool_calls:
                last_error = turn.text
                break
            tool_calls = [(tc.name, tc.args) for tc in turn.tool_calls]
        else:
            if turn.text and not turn.tool_calls:
                last_error = turn.text
                break
            tool_calls = list(turn.tool_calls)

        if not tool_calls:
            last_error = last_error or "模型未回傳工具呼叫"
            break

        tool_results: list[tuple[str, Any]] = []
        for name, args in tool_calls:
            if name == "complete_task":
                result = _handle_complete_task(ctx, intake, args)
                return SchedulerWorkerRunResult(
                    success=result.success,
                    task_id=result.task_id,
                    summary=result.summary,
                    last_run_path=result.last_run_path,
                    turns_used=turns,
                    plan_id=result.plan_id,
                    tasks_planned=result.tasks_planned,
                    error=result.error,
                )
            try:
                out = dispatch_scheduler_tool(ctx, name, args)
            except ToolPolicyError as exc:
                out = json.dumps({"error": str(exc)}, ensure_ascii=False)
            tool_results.append((name, out))

        driver.submit_tool_results(tool_results)

    failed = SchedulerLastRun(
        task_id=intake.task_id,
        status="failed",
        files_changed=list(ctx.files_changed),
        summary=last_error or "超過最大輪次",
        notes_for_reviewer="harness_max_turns",
    )
    path = _write_last_run(ctx.workspace_root, ctx.project_id, ctx.worker_id, failed)
    rel = str(path.relative_to(project_dir(ctx.workspace_root, ctx.project_id)))
    return SchedulerWorkerRunResult(
        success=False,
        task_id=intake.task_id,
        summary=failed.summary,
        last_run_path=rel,
        turns_used=turns,
        error=failed.summary,
    )


def run_scheduler_worker_scripted(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    turns: list[ScriptedAgentTurn],
    *,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> SchedulerWorkerRunResult:
    """測試／示範：不依賴 LLM 的固定 tool 序列。"""
    intake = _load_intake(workspace_root, project_id)
    ctx = SchedulerHarnessToolContext(workspace_root, project_id, worker_id)
    system = SCHEDULER_SYSTEM_PREFIX + f"\n你的 worker_id 是 {worker_id!r}。\n"
    user = _build_user_message(intake, worker_id)

    class _ScriptedWrapper:
        def __init__(self, inner: ScriptedAgentDriver) -> None:
            self._inner = inner

        def start(self, system_instruction: str, user_task: str) -> None:
            del system_instruction, user_task

        def next_turn(self) -> ScriptedAgentTurn | None:
            return self._inner.consume_turn()

        def submit_tool_results(self, results: list[tuple[str, Any]]) -> None:
            del results

    return _run_agent_loop(
        driver=_ScriptedWrapper(ScriptedAgentDriver(turns)),
        system_instruction=system,
        user_task=user,
        ctx=ctx,
        intake=intake,
        max_turns=max_turns,
    )


def load_scheduler_last_run(
    workspace_root: Path, project_id: str, worker_id: str
) -> SchedulerLastRun | None:
    path = (
        project_dir(workspace_root, project_id) / "workers" / worker_id / "last_run.json"
    )
    if not path.is_file():
        return None
    return SchedulerLastRun.model_validate(json.loads(path.read_text(encoding="utf-8")))
