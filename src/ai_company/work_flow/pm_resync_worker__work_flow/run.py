from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.schemas.commands import BaseCommand, CommandType, PmResyncWorkerCommand
from ai_company.schemas.results import PmResyncWorkerResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> PmResyncWorkerResult:
    if not isinstance(command, PmResyncWorkerCommand):
        return PmResyncWorkerResult(success=False, message="指令類型錯誤", error_code="bad_command")
    template = command.template.strip().lower()
    if template not in worker_runner.SUPPORTED_DEFAULT_TEMPLATES:
        supported = ", ".join(sorted(worker_runner.SUPPORTED_DEFAULT_TEMPLATES))
        return PmResyncWorkerResult(
            success=False,
            message=f"不支援的模板 {template!r}；目前支援：{supported}",
            error_code="unknown_template",
        )
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return PmResyncWorkerResult(success=False, message=str(exc), error_code="no_project")

    entry = worker_runner.default_worker_entry_for_template(template)
    root = project_folders.project_dir(deps.workspace_root, project_id)
    project_folders.ensure_project_tree(root)
    worker_runner.copy_worker_default_into_worker_dir(
        root, template, force_package=command.force_package
    )
    return PmResyncWorkerResult(
        success=True,
        message=(
            f"已自 worker_default/{template}/ 重新同步 Worker {entry.id!r} "
            f"（force_package={command.force_package}）"
        ),
        project_id=project_id,
        worker_id=entry.id,
        template=template,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.PM_RESYNC_WORKER,
        flow_id="pm_resync_worker__work_flow",
        description_zh="PM：自 worker_default 重新同步 Worker 種子",
        runner=run,
    )
