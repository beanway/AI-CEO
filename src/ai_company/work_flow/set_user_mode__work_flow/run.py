from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import BaseCommand, CommandType, SetUserModeCommand
from ai_company.schemas.documents import UserMode
from ai_company.schemas.results import SetUserModeResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> SetUserModeResult:
    if not isinstance(command, SetUserModeCommand):
        return SetUserModeResult(success=False, message="指令類型錯誤", error_code="bad_command")
    file_store.ensure_company_dirs(deps.workspace_root)
    if command.mode == UserMode.PM:
        active = file_store.get_active_project(deps.workspace_root)
        if active is None:
            return SetUserModeResult(
                success=False,
                message="切換 PM 前請先 /switch 到專案，或 /newproject 建殼。",
                error_code="no_active_project",
            )
    file_store.set_user_mode(deps.workspace_root, command.telegram_user_id, command.mode)
    label = "PM" if command.mode == UserMode.PM else "CEO"
    extra = ""
    if command.mode == UserMode.PM:
        active = file_store.get_active_project(deps.workspace_root)
        if active:
            extra = f"（專案 {active.id} · {active.name}）"
    return SetUserModeResult(
        success=True,
        message=f"已切換為 {label} 模式{extra}。",
        mode=command.mode.value,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SET_USER_MODE,
        flow_id="set_user_mode__work_flow",
        description_zh="Telegram 使用者 CEO/PM 模式",
        runner=run,
    )
