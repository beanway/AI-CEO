from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner.internal.default_install import (
    SUPPORTED_DEFAULT_TEMPLATES,
    copy_worker_default_into_worker_dir,
    default_worker_entry_for_template,
)
from ai_company.schemas.commands import AddWorkerCommand, BaseCommand, CommandType
from ai_company.schemas.documents import WorkersFile
from ai_company.schemas.results import AddWorkerResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> AddWorkerResult:
    if not isinstance(command, AddWorkerCommand):
        return AddWorkerResult(success=False, message="指令類型錯誤", error_code="bad_command")
    template = command.template.strip().lower()
    if template not in SUPPORTED_DEFAULT_TEMPLATES:
        supported = ", ".join(sorted(SUPPORTED_DEFAULT_TEMPLATES))
        return AddWorkerResult(
            success=False,
            message=f"不支援的模板 {template!r}；目前支援：{supported}",
            error_code="unknown_template",
        )
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return AddWorkerResult(success=False, message=str(exc), error_code="no_project")

    entry = default_worker_entry_for_template(template)
    existing = file_store.load_workers(deps.workspace_root, project_id)
    if any(w.id == entry.id for w in existing.workers):
        return AddWorkerResult(
            success=False,
            message=f"Worker {entry.id!r} 已在 workers.yaml 中",
            error_code="duplicate_worker",
            project_id=project_id,
            worker_id=entry.id,
        )

    root = project_folders.project_dir(deps.workspace_root, project_id)
    project_folders.ensure_project_tree(root)
    merged = WorkersFile(workers=[*existing.workers, entry])
    project_folders.ensure_worker_directories(root, [entry])
    copy_worker_default_into_worker_dir(root, template)
    file_store.save_workers(deps.workspace_root, project_id, merged)

    return AddWorkerResult(
        success=True,
        message=(
            f"已加入 Worker {entry.id!r}（kind={entry.kind}），"
            f"並自 worker_default/{template}/ 複製 SKILL 與 skills/"
        ),
        project_id=project_id,
        worker_id=entry.id,
        kind=entry.kind,
        template=template,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.ADD_WORKER,
        flow_id="add_worker__work_flow",
        description_zh="PM：從 worker_default 加入單一 Worker",
        runner=run,
    )
