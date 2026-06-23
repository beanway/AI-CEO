from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_workspace import core as setup_workspace
from ai_company.schemas.commands import (
    BaseCommand,
    CommandType,
    UpdateGlobalConfigCommand,
)
from ai_company.schemas.documents import GlobalConfigFile
from ai_company.schemas.results import UpdateGlobalConfigResult
from ai_company.work_flow.registry import WorkFlowRegistry


def _merge_config(
    current: GlobalConfigFile,
    command: UpdateGlobalConfigCommand,
) -> GlobalConfigFile:
    updates: dict = {}
    if command.default_model is not None:
        model = command.default_model.strip()
        if not model:
            raise ValueError("default_model 不可為空白")
        updates["default_model"] = model
    if command.notification_policy is not None:
        updates["notification_policy"] = command.notification_policy
    if command.max_output_tokens is not None:
        updates["max_output_tokens"] = command.max_output_tokens
    if command.thinking_budget is not None:
        updates["thinking_budget"] = command.thinking_budget
    if command.include_thoughts is not None:
        updates["include_thoughts"] = command.include_thoughts
    if command.temperature is not None:
        updates["temperature"] = command.temperature
    return current.model_copy(update=updates)


def run(command: BaseCommand, deps: AppDeps) -> UpdateGlobalConfigResult:
    if not isinstance(command, UpdateGlobalConfigCommand):
        return UpdateGlobalConfigResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    setup_workspace.ensure_workspace(deps.workspace_root)
    current = file_store.load_global_config(deps.workspace_root)
    try:
        merged = _merge_config(current, command)
    except ValueError as exc:
        return UpdateGlobalConfigResult(
            success=False,
            message=str(exc),
            error_code="invalid_config",
        )
    file_store.save_global_config(deps.workspace_root, merged)
    lines = [
        "已更新 global_config.yaml",
        f"  default_model: {merged.default_model}",
        f"  notification_policy: {merged.notification_policy.value}",
        f"  max_output_tokens: {merged.max_output_tokens}",
        f"  thinking_budget: {merged.thinking_budget}",
        f"  include_thoughts: {merged.include_thoughts}",
    ]
    if merged.temperature is not None:
        lines.append(f"  temperature: {merged.temperature}")
    return UpdateGlobalConfigResult(success=True, message="\n".join(lines))


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.UPDATE_GLOBAL_CONFIG,
        flow_id="update_global_config__work_flow",
        description_zh="CEO 更新 global_config（模型、通知、AI 參數）",
        runner=run,
    )
