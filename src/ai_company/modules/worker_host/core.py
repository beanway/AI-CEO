"""載入沙盒 worker package 並執行 entrypoint。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_company.modules.worker_host.internal.health import WorkerHealthIssue, check_worker_health
from ai_company.modules.worker_host.internal.manifest import (
    fixtures_seed_root,
    import_entrypoint,
    import_fixtures_entrypoint,
    load_manifest,
)
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.schemas.ai_generation import AiGenerationSettings
from ai_company.schemas.workspace_paths import project_dir

DEFAULT_MAX_TURNS = 25

copy_worker_default_into_worker_dir = worker_runner.copy_worker_default_into_worker_dir
copy_fixtures_package_into_project = worker_runner.copy_fixtures_package_into_project


@dataclass(frozen=True)
class BackendWorkerRunResult:
    success: bool
    task_id: str
    summary: str
    last_run_path: str
    turns_used: int
    error: str | None = None


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


def _dict_to_backend_result(data: dict) -> BackendWorkerRunResult:
    return BackendWorkerRunResult(
        success=bool(data.get("success")),
        task_id=str(data.get("task_id", "")),
        summary=str(data.get("summary", "")),
        last_run_path=str(data.get("last_run_path", "")),
        turns_used=int(data.get("turns_used", 0)),
        error=data.get("error"),
    )


def _dict_to_scheduler_result(data: dict) -> SchedulerWorkerRunResult:
    return SchedulerWorkerRunResult(
        success=bool(data.get("success")),
        task_id=str(data.get("task_id", "")),
        summary=str(data.get("summary", "")),
        last_run_path=str(data.get("last_run_path", "")),
        turns_used=int(data.get("turns_used", 0)),
        plan_id=data.get("plan_id"),
        tasks_planned=int(data.get("tasks_planned", 0)),
        error=data.get("error"),
    )


def has_backend_task(workspace_root: Path, project_id: str) -> bool:
    path = project_dir(workspace_root, project_id) / "pm" / "backend_current_task.yaml"
    return path.is_file()


def has_scheduler_intake(workspace_root: Path, project_id: str) -> bool:
    path = project_dir(workspace_root, project_id) / "pm" / "scheduler_intake.yaml"
    return path.is_file()


def run_backend_scripted(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    turns: list[Any],
    *,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> BackendWorkerRunResult:
    manifest = load_manifest(workspace_root, project_id, worker_id)
    mod = import_entrypoint(workspace_root, project_id, worker_id, manifest)
    fn = getattr(mod, manifest.scripted_entry)
    session = worker_runner.BackendHostSession(workspace_root, project_id, worker_id)
    data = fn(session, turns, max_turns=max_turns)
    return _dict_to_backend_result(data)


def run_scheduler_scripted(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    turns: list[Any],
    *,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> SchedulerWorkerRunResult:
    manifest = load_manifest(workspace_root, project_id, worker_id)
    mod = import_entrypoint(workspace_root, project_id, worker_id, manifest)
    fn = getattr(mod, manifest.scripted_entry)
    session = worker_runner.SchedulerHostSession(workspace_root, project_id, worker_id)
    data = fn(session, turns, max_turns=max_turns)
    return _dict_to_scheduler_result(data)


def run_backend_execution_step(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> BackendWorkerRunResult:
    manifest = load_manifest(workspace_root, project_id, worker_id)
    mod = import_entrypoint(workspace_root, project_id, worker_id, manifest)
    fn = getattr(mod, manifest.execution_step_entry)
    session = worker_runner.BackendHostSession(workspace_root, project_id, worker_id)
    data = fn(session)
    return _dict_to_backend_result(data)


def run_scheduler_execution_step(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> SchedulerWorkerRunResult:
    manifest = load_manifest(workspace_root, project_id, worker_id)
    mod = import_entrypoint(workspace_root, project_id, worker_id, manifest)
    fn = getattr(mod, manifest.execution_step_entry)
    session = worker_runner.SchedulerHostSession(workspace_root, project_id, worker_id)
    data = fn(session)
    return _dict_to_scheduler_result(data)


def load_demo_scenario(project_root: Path, scenario: str) -> list[str]:
    mod = import_fixtures_entrypoint(project_root)
    host = worker_runner.FixturesHost(project_root, fixtures_seed_root())
    fn = getattr(mod, "load_demo_scenario")
    return list(fn(host, scenario))


def install_fixtures_package(project_root: Path, *, force_package: bool = True) -> Path:
    return worker_runner.copy_fixtures_package_into_project(project_root, force_package=force_package)


def audit_workers(
    workspace_root: Path,
    project_id: str,
    worker_ids: list[str],
) -> list[WorkerHealthIssue]:
    issues: list[WorkerHealthIssue] = []
    for wid in worker_ids:
        issues.extend(check_worker_health(workspace_root, project_id, wid))
    return issues


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
    """Gemini 仍由 worker_runner 單體迴圈執行（過渡）；package 用於 scripted／execution_step。"""
    from ai_company.modules.worker_runner import core as worker_runner

    return worker_runner._run_backend_worker_gemini_impl(
        workspace_root,
        project_id,
        worker_id,
        api_key=api_key,
        model=model,
        generation=generation,
        max_turns=max_turns,
    )


__all__ = [
    "BackendWorkerRunResult",
    "SchedulerWorkerRunResult",
    "WorkerHealthIssue",
    "audit_workers",
    "copy_fixtures_package_into_project",
    "copy_worker_default_into_worker_dir",
    "has_backend_task",
    "has_scheduler_intake",
    "install_fixtures_package",
    "load_demo_scenario",
    "run_backend_execution_step",
    "run_backend_scripted",
    "run_backend_worker_gemini",
    "run_scheduler_execution_step",
    "run_scheduler_scripted",
]
