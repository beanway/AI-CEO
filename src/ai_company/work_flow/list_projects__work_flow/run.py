from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.format_messages.core import format_projects_message
from ai_company.schemas.commands import BaseCommand, CommandType, ListProjectsCommand
from ai_company.schemas.results import ListProjectsResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ListProjectsResult:
    if not isinstance(command, ListProjectsCommand):
        return ListProjectsResult(success=False, message="指令類型錯誤", error_code="bad_command")
    pf = file_store.load_projects(deps.workspace_root)
    return ListProjectsResult(success=True, message=format_projects_message(pf))


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.LIST_PROJECTS,
        flow_id="list_projects__work_flow",
        description_zh="列出專案與 active",
        runner=run,
    )
