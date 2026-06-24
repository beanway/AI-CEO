from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.work_flow._shared.company_workspace import ensure_company_workspace
from ai_company.schemas.commands import BaseCommand, CommandType, ShowGlobalConfigCommand
from ai_company.schemas.results import ShowGlobalConfigResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ShowGlobalConfigResult:
    if not isinstance(command, ShowGlobalConfigCommand):
        return ShowGlobalConfigResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    ensure_company_workspace(deps.workspace_root)
    skills = file_store.load_global_skills(deps.workspace_root)
    config = file_store.load_global_config(deps.workspace_root)
    lines = ["global_skills.yaml"]
    if skills.enabled_skill_ids:
        for sid in skills.enabled_skill_ids:
            lines.append(f"  - {sid}")
    else:
        lines.append("  （無啟用 skill）")
    lines.append("")
    lines.append("global_config.yaml")
    lines.append(f"  default_model: {config.default_model}")
    lines.append(f"  notification_policy: {config.notification_policy.value}")
    lines.append(f"  max_output_tokens: {config.max_output_tokens}")
    lines.append(f"  thinking_budget: {config.thinking_budget}")
    lines.append(f"  include_thoughts: {config.include_thoughts}")
    if config.temperature is not None:
        lines.append(f"  temperature: {config.temperature}")
    return ShowGlobalConfigResult(success=True, message="\n".join(lines))


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SHOW_GLOBAL_CONFIG,
        flow_id="show_global_config__work_flow",
        description_zh="顯示 global_skills / global_config",
        runner=run,
    )
