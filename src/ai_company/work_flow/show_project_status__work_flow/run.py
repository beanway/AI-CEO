from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.schemas.commands import BaseCommand, CommandType, ShowProjectStatusCommand
from ai_company.schemas.results import ShowProjectStatusResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ShowProjectStatusResult:
    if not isinstance(command, ShowProjectStatusCommand):
        return ShowProjectStatusResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return ShowProjectStatusResult(
            success=False, message=str(exc), error_code="no_project"
        )
    pf = file_store.load_projects(deps.workspace_root)
    rec = next((p for p in pf.projects if p.id == project_id), None)
    name = rec.name if rec else "?"
    root = project_folders.project_dir(deps.workspace_root, project_id)
    workers = file_store.load_workers(deps.workspace_root, project_id)
    skills = file_store.load_project_skills(deps.workspace_root, project_id)
    req = root / "shared" / "requirements.md"
    req_hint = "有" if req.is_file() else "無"
    worker_lines = (
        "\n".join(f"  - {w.id} ({w.kind})" for w in workers.workers)
        if workers.workers
        else "  （尚未建局）"
    )
    skill_lines = (
        ", ".join(skills.enabled_skill_ids) if skills.enabled_skill_ids else "（無）"
    )
    pm_dir = root / "pm"
    pm_files = len(list(pm_dir.iterdir())) if pm_dir.is_dir() else 0
    harness = file_store.load_project_harness_state(deps.workspace_root, project_id)
    lifecycle = harness.lifecycle.value
    message = (
        f"專案 {project_id} · {name}\n"
        f"harness：{lifecycle}\n"
        f"requirements.md：{req_hint}\n"
        f"pm/ 檔案數：{pm_files}\n"
        f"Workers（workers.yaml）：\n{worker_lines}\n"
        f"專案 skills：{skill_lines}"
    )
    return ShowProjectStatusResult(
        success=True,
        message=message,
        project_id=project_id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SHOW_PROJECT_STATUS,
        flow_id="show_project_status__work_flow",
        description_zh="PM 專案狀態摘要（讀取為主）",
        runner=run,
    )
