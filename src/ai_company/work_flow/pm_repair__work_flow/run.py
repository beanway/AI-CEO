from __future__ import annotations

from datetime import datetime, timezone

from ai_company.app_deps import AppDeps
from ai_company.modules.execution_store import core as execution_store
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_host import core as worker_host
from ai_company.schemas.commands import BaseCommand, CommandType, PmRepairCommand
from ai_company.schemas.documents import ExecutionStatus
from ai_company.schemas.results import PmRepairResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def _append_repair_log(project_root, line: str) -> None:
    log_path = project_root / "pm" / "repair_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(command: BaseCommand, deps: AppDeps) -> PmRepairResult:
    if not isinstance(command, PmRepairCommand):
        return PmRepairResult(success=False, message="指令類型錯誤", error_code="bad_command")
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return PmRepairResult(success=False, message=str(exc), error_code="no_project")
    root = project_folders.project_dir(deps.workspace_root, project_id)
    project_folders.ensure_project_tree(root)
    running = execution_store.list_running_for_project(deps.workspace_root, project_id)
    interrupted_ids: list[str] = []
    if command.interrupt and running:
        for state in running:
            updated = execution_store.interrupt_execution(deps.workspace_root, state.execution_id)
            if updated is not None and updated.status == ExecutionStatus.INTERRUPTED:
                interrupted_ids.append(updated.execution_id)
        running = execution_store.list_running_for_project(deps.workspace_root, project_id)
    workers = file_store.load_workers(deps.workspace_root, project_id)
    health = worker_host.audit_workers(
        deps.workspace_root,
        project_id,
        [w.id for w in workers.workers],
    )
    health_lines = (
        "\n".join(f"  - {h.worker_id}: [{h.code}] {h.detail}" for h in health)
        if health
        else "  （無健檢問題）"
    )
    skills = file_store.load_project_skills(deps.workspace_root, project_id)
    pm_dir = root / "pm"
    pm_count = len(list(pm_dir.iterdir())) if pm_dir.is_dir() else 0
    shared_dir = root / "shared"
    shared_count = len(list(shared_dir.iterdir())) if shared_dir.is_dir() else 0
    run_lines = (
        "\n".join(f"  - {s.execution_id} worker={s.worker_id or '?'} " for s in running)
        if running
        else "  （無進行中 execution）"
    )
    ts = datetime.now(timezone.utc).isoformat()
    action = "interrupt" if command.interrupt else "inspect"
    _append_repair_log(
        root,
        f'{{"at":"{ts}","action":"{action}","running":{len(running)},"interrupted":{len(interrupted_ids)}}}',
    )
    interrupt_note = ""
    if interrupted_ids:
        interrupt_note = f"\n已手動中斷：{', '.join(interrupted_ids)}"
    message = (
        f"維修摘要 · 專案 {project_id}\n"
        f"pm/ 檔案：{pm_count} · shared/ 檔案：{shared_count}\n"
        f"Workers：{len(workers.workers)} · 專案 skills：{len(skills.enabled_skill_ids)}\n"
        f"Worker 健檢（{len(health)} 項）：\n{health_lines}\n"
        f"進行中 execution：\n{run_lines}{interrupt_note}"
    )
    return PmRepairResult(
        success=True,
        message=message,
        project_id=project_id,
        running_execution_count=len(running),
        interrupted_execution_ids=interrupted_ids,
        health_issue_count=len(health),
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.PM_REPAIR,
        flow_id="pm_repair__work_flow",
        description_zh="PM 維修摘要與 execution 手動中斷",
        runner=run,
    )
