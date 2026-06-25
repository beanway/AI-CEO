"""backend Worker 執行：Skill harness + Agent 迴圈。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

from ai_company.modules.sandbox_runner.core import ToolPolicyError
from ai_company.modules.worker_runner.internal.contracts import (
    BackendLastRun,
    BackendTaskContract,
    BackendTestResult,
    SchedulerIntakeContract,
)
from ai_company.modules.worker_runner.internal.default_install import (
    SUPPORTED_DEFAULT_TEMPLATES,
    copy_fixtures_package_into_project,
    copy_worker_default_into_worker_dir,
    default_worker_entry_for_template,
)
from ai_company.modules.worker_runner.internal.host_session import (
    BackendHostSession,
    FixturesHost,
    SchedulerHostSession,
)
from ai_company.modules.worker_runner.internal.gemini_agent import GeminiAgentDriver
from ai_company.modules.worker_runner.internal.harness_tools import (
    HarnessToolContext,
    dispatch_tool,
)
from ai_company.modules.worker_runner.internal.scripted_agent import (
    PlannedToolCall,
    ScriptedAgentDriver,
    ScriptedAgentTurn,
)
from ai_company.modules.worker_runner.internal.scheduler_runner import (
    SchedulerWorkerRunResult,
    load_scheduler_last_run,
    run_scheduler_worker_scripted,
)
from ai_company.modules.worker_runner.internal.seed import (
    seed_backend_worker_project,
    seed_scheduler_backend_demo_project,
    worker_default_fixtures_dir,
)
from ai_company.schemas.ai_generation import AiGenerationSettings
from ai_company.schemas.workspace_paths import project_dir

DEFAULT_MAX_TURNS = 25

BACKEND_SYSTEM_PREFIX = """你是專案沙盒內的後端 AI 執行者（backend Worker）。
工作目錄為專案根（projects/<id>/）。收到任務後：
1. 用 list_skills / read_skill 閱讀 workers/<worker_id>/skills/ 劇本並遵循步驟。
2. 用 read_file / write_file 與 run_terminal 完成實作與測試。
3. 測試通過後呼叫 complete_task（status=success, test_exit_code=0）。
禁止 pip install、任意 shell、修改框架 src/。
"""


@dataclass(frozen=True)
class BackendWorkerRunResult:
    success: bool
    task_id: str
    summary: str
    last_run_path: str
    turns_used: int
    error: str | None = None


class _AgentDriver(Protocol):
    def start(self, system_instruction: str, user_task: str) -> None: ...

    def next_turn(self) -> Any: ...

    def submit_tool_results(self, results: list[tuple[str, Any]]) -> None: ...


def _load_task(workspace_root: Path, project_id: str) -> BackendTaskContract:
    path = project_dir(workspace_root, project_id) / "pm" / "backend_current_task.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"缺少任務契約：{path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return BackendTaskContract.model_validate(raw)


def _build_user_message(task: BackendTaskContract, worker_id: str) -> str:
    lines = [
        f"task_id: {task.task_id}",
        f"worker_id: {worker_id}",
        "",
        "goal:",
        task.goal.strip(),
        "",
        "acceptance_criteria:",
    ]
    lines.extend(f"- {c}" for c in task.acceptance_criteria)
    if task.context_refs:
        lines.append("")
        lines.append("context_refs:")
        lines.extend(f"- {r}" for r in task.context_refs)
    lines.append("")
    lines.append("請開始：先 list_skills，再依劇本執行。")
    return "\n".join(lines)


def _write_last_run(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    payload: BackendLastRun,
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
    ctx: HarnessToolContext,
    task: BackendTaskContract,
    args: dict,
) -> BackendWorkerRunResult:
    status = str(args.get("status", "failed"))
    summary = str(args.get("summary", ""))
    test_command = str(args.get("test_command", ""))
    test_exit = int(args.get("test_exit_code", 1))
    notes = str(args.get("notes_for_reviewer", ""))

    if status == "success" and test_exit != 0:
        status = "failed"
        summary = f"complete_task 宣告 success 但 test_exit_code={test_exit}"

    last = BackendLastRun(
        task_id=task.task_id,
        status=status,
        files_changed=list(ctx.files_changed),
        test_result=BackendTestResult(command=test_command, exit_code=test_exit)
        if test_command
        else None,
        summary=summary,
        notes_for_reviewer=notes,
    )
    path = _write_last_run(ctx.workspace_root, ctx.project_id, ctx.worker_id, last)
    rel = str(path.relative_to(project_dir(ctx.workspace_root, ctx.project_id)))
    ok = status == "success"
    return BackendWorkerRunResult(
        success=ok,
        task_id=task.task_id,
        summary=summary,
        last_run_path=rel,
        turns_used=0,
        error=None if ok else summary,
    )


def _run_agent_loop(
    *,
    driver: _AgentDriver,
    system_instruction: str,
    user_task: str,
    ctx: HarnessToolContext,
    task: BackendTaskContract,
    max_turns: int,
) -> BackendWorkerRunResult:
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
                result = _handle_complete_task(ctx, task, args)
                return BackendWorkerRunResult(
                    success=result.success,
                    task_id=result.task_id,
                    summary=result.summary,
                    last_run_path=result.last_run_path,
                    turns_used=turns,
                    error=result.error,
                )
            try:
                out = dispatch_tool(ctx, name, args)
            except ToolPolicyError as exc:
                out = json.dumps({"error": str(exc)}, ensure_ascii=False)
            tool_results.append((name, out))

        driver.submit_tool_results(tool_results)

    failed = BackendLastRun(
        task_id=task.task_id,
        status="failed",
        files_changed=list(ctx.files_changed),
        summary=last_error or "超過最大輪次",
        notes_for_reviewer="harness_max_turns",
    )
    path = _write_last_run(ctx.workspace_root, ctx.project_id, ctx.worker_id, failed)
    rel = str(path.relative_to(project_dir(ctx.workspace_root, ctx.project_id)))
    return BackendWorkerRunResult(
        success=False,
        task_id=task.task_id,
        summary=failed.summary,
        last_run_path=rel,
        turns_used=turns,
        error=failed.summary,
    )


def run_backend_worker_scripted(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    turns: list[ScriptedAgentTurn],
    *,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> BackendWorkerRunResult:
    """測試／示範：不依賴 LLM 的固定 tool 序列。"""
    from ai_company.modules.worker_host import core as worker_host

    return worker_host.run_backend_scripted(
        workspace_root, project_id, worker_id, turns, max_turns=max_turns
    )


def run_backend_worker_gemini(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    *,
    api_key: str,
    model: str,
    generation: AiGenerationSettings,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> BackendWorkerRunResult:
    """使用 Gemini function calling 執行 backend 任務。"""
    return _run_backend_worker_gemini_impl(
        workspace_root,
        project_id,
        worker_id,
        api_key=api_key,
        model=model,
        generation=generation,
        max_turns=max_turns,
    )


def _run_backend_worker_gemini_impl(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    *,
    api_key: str,
    model: str,
    generation: AiGenerationSettings,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> BackendWorkerRunResult:
    task = _load_task(workspace_root, project_id)
    ctx = HarnessToolContext(workspace_root, project_id, worker_id)
    system = BACKEND_SYSTEM_PREFIX + f"\n你的 worker_id 是 {worker_id!r}。\n"
    user = _build_user_message(task, worker_id)
    driver = GeminiAgentDriver(api_key, model=model, generation=generation)
    return _run_agent_loop(
        driver=driver,
        system_instruction=system,
        user_task=user,
        ctx=ctx,
        task=task,
        max_turns=max_turns,
    )


def load_last_run(
    workspace_root: Path, project_id: str, worker_id: str
) -> BackendLastRun | None:
    path = (
        project_dir(workspace_root, project_id) / "workers" / worker_id / "last_run.json"
    )
    if not path.is_file():
        return None
    return BackendLastRun.model_validate(json.loads(path.read_text(encoding="utf-8")))


__all__ = [
    "BackendTaskContract",
    "BackendWorkerRunResult",
    "PlannedToolCall",
    "SUPPORTED_DEFAULT_TEMPLATES",
    "SchedulerIntakeContract",
    "SchedulerWorkerRunResult",
    "ScriptedAgentTurn",
    "copy_fixtures_package_into_project",
    "copy_worker_default_into_worker_dir",
    "default_worker_entry_for_template",
    "BackendHostSession",
    "SchedulerHostSession",
    "FixturesHost",
    "load_last_run",
    "load_scheduler_last_run",
    "run_backend_worker_gemini",
    "run_backend_worker_scripted",
    "run_scheduler_worker_scripted",
    "seed_backend_worker_project",
    "seed_scheduler_backend_demo_project",
    "worker_default_fixtures_dir",
]
