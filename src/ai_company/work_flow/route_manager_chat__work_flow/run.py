from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import (
    BaseCommand,
    CeoChatCommand,
    CommandType,
    PmChatCommand,
    RouteManagerChatCommand,
)
from ai_company.schemas.documents import UserMode
from ai_company.schemas.results import FlowResult
from ai_company.work_flow.ceo_chat__work_flow.run import run as run_ceo_chat
from ai_company.work_flow.pm_chat__work_flow.run import run as run_pm_chat
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> FlowResult:
    if not isinstance(command, RouteManagerChatCommand):
        return FlowResult(success=False, message="指令類型錯誤", error_code="bad_command")
    text = command.text.strip()
    if not text:
        return FlowResult(success=False, message="訊息不可為空白", error_code="invalid_text")
    mode = file_store.get_user_mode(deps.workspace_root, command.telegram_user_id)
    if mode == UserMode.PM:
        return run_pm_chat(
            PmChatCommand(channel=command.channel, text=text),
            deps,
        )
    return run_ceo_chat(
        CeoChatCommand(channel=command.channel, text=text),
        deps,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.ROUTE_MANAGER_CHAT,
        flow_id="route_manager_chat__work_flow",
        description_zh="TG 文字：依 mode 轉 CEO／PM chat",
        runner=run,
    )
