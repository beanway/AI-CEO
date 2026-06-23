from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.schemas.commands import BaseCommand, CommandType, SetupWorkersCommand
from ai_company.schemas.documents import WorkerEntry, WorkersFile
from ai_company.schemas.results import SetupWorkersResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def _resolve_workers(command: SetupWorkersCommand) -> list[WorkerEntry]:
    if command.template is not None:
        return list(project_folders.WORKER_TEMPLATES[command.template])
    assert command.workers is not None
    return list(command.workers)


def _validate_worker_ids(workers: list[WorkerEntry]) -> str | None:
    seen: set[str] = set()
    for entry in workers:
        if entry.id in seen:
            return f"重複的 worker id：{entry.id!r}"
        seen.add(entry.id)
        if "/" in entry.id or entry.id.startswith("."):
            return f"無效的 worker id：{entry.id!r}"
    return None


def _validate_custom_skills(root, workers: list[WorkerEntry]) -> str | None:
    for entry in workers:
        if project_folders.is_builtin_kind(entry.kind):
            continue
        skill_path = root / "workers" / entry.id / "SKILL.md"
        if not skill_path.is_file():
            return (
                f"自訂 kind {entry.kind!r} 需在 {skill_path.relative_to(root)} 定義能力"
            )
    return None


def run(command: BaseCommand, deps: AppDeps) -> SetupWorkersResult:
    if not isinstance(command, SetupWorkersCommand):
        return SetupWorkersResult(success=False, message="指令類型錯誤", error_code="bad_command")
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return SetupWorkersResult(success=False, message=str(exc), error_code="no_project")
    workers = _resolve_workers(command)
    err = _validate_worker_ids(workers)
    if err:
        return SetupWorkersResult(success=False, message=err, error_code="invalid_workers")
    root = project_folders.project_dir(deps.workspace_root, project_id)
    project_folders.ensure_project_tree(root)
    project_folders.ensure_worker_directories(root, workers)
    err = _validate_custom_skills(root, workers)
    if err:
        return SetupWorkersResult(success=False, message=err, error_code="missing_skill_md")
    file_store.save_workers(deps.workspace_root, project_id, WorkersFile(workers=workers))
    ids = ", ".join(w.id for w in workers)
    return SetupWorkersResult(
        success=True,
        message=f"專案 {project_id} 已寫入 workers.yaml（{len(workers)} 個）：{ids}",
        project_id=project_id,
        worker_count=len(workers),
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SETUP_WORKERS,
        flow_id="setup_workers__work_flow",
        description_zh="PM 建局：workers.yaml 與 workers/<id>/",
        runner=run,
    )
