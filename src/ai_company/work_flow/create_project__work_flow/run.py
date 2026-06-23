from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.schemas.commands import BaseCommand, CommandType, CreateProjectCommand
from ai_company.schemas.results import CreateProjectResult
from ai_company.work_flow._shared.create_project_shell import create_project_shell
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> CreateProjectResult:
    if not isinstance(command, CreateProjectCommand):
        return CreateProjectResult(success=False, message="指令類型錯誤", error_code="bad_command")
    name = command.name.strip()
    if not name:
        return CreateProjectResult(
            success=False,
            message="專案名稱不可為空白",
            error_code="invalid_name",
        )
    try:
        rec = create_project_shell(
            deps,
            name,
            initial_requirements=command.initial_requirements,
        )
    except Exception as exc:
        return CreateProjectResult(
            success=False,
            message=f"建專案失敗：{exc}",
            error_code="create_failed",
        )
    return CreateProjectResult(
        success=True,
        message=f"已建立專案殼 → id={rec.id}（{rec.name}）\nPM Session 索引：sessions/pm_{rec.id}.json",
        project_id=rec.id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.CREATE_PROJECT,
        flow_id="create_project__work_flow",
        description_zh="CEO 建專案殼（目錄、索引、PM Session）",
        runner=run,
    )
