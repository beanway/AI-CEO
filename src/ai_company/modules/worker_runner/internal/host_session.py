"""Host session：供沙盒 package 透過 duck typing 呼叫。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ai_company.modules.sandbox_runner.core import ToolPolicyError
from ai_company.modules.worker_runner.internal.contracts import (
    BackendLastRun,
    BackendTaskContract,
    BackendTestResult,
    SchedulerIntakeContract,
    SchedulerLastRun,
    TaskQueuePlan,
)
from ai_company.modules.worker_runner.internal.harness_tools import (
    HarnessToolContext,
    dispatch_tool,
)
from ai_company.modules.worker_runner.internal.scheduler_harness_tools import (
    SchedulerHarnessToolContext,
    dispatch_scheduler_tool,
)
from ai_company.schemas.workspace_paths import project_dir


@dataclass
class BackendHostSession:
    workspace_root: Path
    project_id: str
    worker_id: str
    files_changed: list[str] = field(default_factory=list)

    def _ctx(self) -> HarnessToolContext:
        ctx = HarnessToolContext(self.workspace_root, self.project_id, self.worker_id)
        ctx.files_changed = self.files_changed
        return ctx

    def dispatch_tool(self, name: str, args: dict) -> str:
        try:
            return dispatch_tool(self._ctx(), name, args)
        except ToolPolicyError as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def load_task(self) -> dict:
        path = project_dir(self.workspace_root, self.project_id) / "pm" / "backend_current_task.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"缺少任務契約：{path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return dict(raw)

    def _write_last_run(self, payload: BackendLastRun) -> str:
        path = (
            project_dir(self.workspace_root, self.project_id)
            / "workers"
            / self.worker_id
            / "last_run.json"
        )
        path.write_text(
            json.dumps(payload.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(path.relative_to(project_dir(self.workspace_root, self.project_id)))

    def complete_task(self, task: dict, args: dict) -> dict:
        contract = BackendTaskContract.model_validate(task)
        status = str(args.get("status", "failed"))
        summary = str(args.get("summary", ""))
        test_command = str(args.get("test_command", ""))
        test_exit = int(args.get("test_exit_code", 1))
        notes = str(args.get("notes_for_reviewer", ""))
        if status == "success" and test_exit != 0:
            status = "failed"
            summary = f"complete_task 宣告 success 但 test_exit_code={test_exit}"
        last = BackendLastRun(
            task_id=contract.task_id,
            status=status,
            files_changed=list(self.files_changed),
            test_result=BackendTestResult(command=test_command, exit_code=test_exit)
            if test_command
            else None,
            summary=summary,
            notes_for_reviewer=notes,
        )
        rel = self._write_last_run(last)
        ok = status == "success"
        return {
            "success": ok,
            "task_id": contract.task_id,
            "summary": summary,
            "last_run_path": rel,
            "error": None if ok else summary,
        }

    def fail_task(self, task: dict, summary: str, turns: int) -> dict:
        contract = BackendTaskContract.model_validate(task)
        last = BackendLastRun(
            task_id=contract.task_id,
            status="failed",
            files_changed=list(self.files_changed),
            summary=summary,
            notes_for_reviewer="harness_max_turns",
        )
        rel = self._write_last_run(last)
        return {
            "success": False,
            "task_id": contract.task_id,
            "summary": summary,
            "last_run_path": rel,
            "turns_used": turns,
            "error": summary,
        }


@dataclass
class SchedulerHostSession:
    workspace_root: Path
    project_id: str
    worker_id: str
    files_changed: list[str] = field(default_factory=list)

    def _ctx(self) -> SchedulerHarnessToolContext:
        ctx = SchedulerHarnessToolContext(self.workspace_root, self.project_id, self.worker_id)
        ctx.files_changed = self.files_changed
        return ctx

    def dispatch_tool(self, name: str, args: dict) -> str:
        try:
            return dispatch_scheduler_tool(self._ctx(), name, args)
        except ToolPolicyError as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    def load_intake(self) -> dict:
        path = project_dir(self.workspace_root, self.project_id) / "pm" / "scheduler_intake.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"缺少 intake：{path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return dict(raw)

    def _load_task_queue(self) -> TaskQueuePlan:
        path = project_dir(self.workspace_root, self.project_id) / "pm" / "task_queue.yaml"
        if not path.is_file():
            raise FileNotFoundError("缺少 pm/task_queue.yaml")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return TaskQueuePlan.model_validate(raw)

    def _write_last_run(self, payload: SchedulerLastRun) -> str:
        path = (
            project_dir(self.workspace_root, self.project_id)
            / "workers"
            / self.worker_id
            / "last_run.json"
        )
        path.write_text(
            json.dumps(payload.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(path.relative_to(project_dir(self.workspace_root, self.project_id)))

    def complete_task(self, intake: dict, args: dict) -> dict:
        contract = SchedulerIntakeContract.model_validate(intake)
        status = str(args.get("status", "failed"))
        summary = str(args.get("summary", ""))
        notes = str(args.get("notes_for_reviewer", ""))
        plan_id: str | None = None
        tasks_planned = 0
        if status == "success":
            try:
                plan = self._load_task_queue()
                plan_id = plan.plan_id
                tasks_planned = len(plan.tasks)
                if tasks_planned < 1:
                    status = "failed"
                    summary = "task_queue.yaml 無任務"
            except Exception as exc:
                status = "failed"
                summary = f"無法驗證 task_queue：{exc}"
        last = SchedulerLastRun(
            task_id=contract.task_id,
            status=status,
            files_changed=list(self.files_changed),
            summary=summary,
            notes_for_reviewer=notes,
            plan_id=plan_id,
            tasks_planned=tasks_planned,
        )
        rel = self._write_last_run(last)
        ok = status == "success"
        return {
            "success": ok,
            "task_id": contract.task_id,
            "summary": summary,
            "last_run_path": rel,
            "plan_id": plan_id,
            "tasks_planned": tasks_planned,
            "error": None if ok else summary,
        }

    def fail_task(self, intake: dict, summary: str, turns: int) -> dict:
        contract = SchedulerIntakeContract.model_validate(intake)
        last = SchedulerLastRun(
            task_id=contract.task_id,
            status="failed",
            files_changed=list(self.files_changed),
            summary=summary,
            notes_for_reviewer="harness_max_turns",
        )
        rel = self._write_last_run(last)
        return {
            "success": False,
            "task_id": contract.task_id,
            "summary": summary,
            "last_run_path": rel,
            "turns_used": turns,
            "error": summary,
        }


class FixturesHost:
    def __init__(self, project_root: Path, fixtures_seed_root: Path) -> None:
        self.project_root = project_root
        self.fixtures_seed_root = fixtures_seed_root
