from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.schemas.commands import BaseCommand, CommandType, SwitchProjectCommand
from ai_company.schemas.results import SwitchProjectResult
from ai_company.work_flow._shared.legacy_services import company_service
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> SwitchProjectResult:
    if not isinstance(command, SwitchProjectCommand):
        return SwitchProjectResult(success=False, message="指令類型錯誤", error_code="bad_command")
    company = company_service(deps)
    try:
        rec = company.set_active_project(command.project_id)
    except ValueError as exc:
        return SwitchProjectResult(
            success=False,
            message=str(exc),
            error_code="project_not_found",
        )
    return SwitchProjectResult(
        success=True,
        message=f"已切換 active 專案 → {rec.id}（{rec.name}）",
        project_id=rec.id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SWITCH_PROJECT,
        flow_id="switch_project__work_flow",
        description_zh="切換 active 專案",
        runner=run,
    )
