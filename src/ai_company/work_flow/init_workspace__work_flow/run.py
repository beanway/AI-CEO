from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_workspace import core as setup_workspace
from ai_company.schemas.commands import BaseCommand, CommandType, InitWorkspaceCommand
from ai_company.schemas.results import FlowResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> FlowResult:
    if not isinstance(command, InitWorkspaceCommand):
        return FlowResult(success=False, message="指令類型錯誤", error_code="bad_command")
    setup_workspace.ensure_workspace(deps.workspace_root)
    file_store.bootstrap_default_project_if_needed(deps.workspace_root)
    return FlowResult(
        success=True,
        message=f"已建立沙盒：{deps.workspace_root}",
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.INIT_WORKSPACE,
        flow_id="init_workspace__work_flow",
        description_zh="建立工作區根與預設索引檔",
        runner=run,
    )
