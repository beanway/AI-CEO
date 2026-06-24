from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.schemas.commands import BaseCommand, CommandType, ListRegistrySkillsCommand
from ai_company.schemas.results import ListRegistrySkillsResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ListRegistrySkillsResult:
    del deps
    if not isinstance(command, ListRegistrySkillsCommand):
        return ListRegistrySkillsResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    ids = skill_registry.find_registered_skills(query=command.query)
    lines = "\n".join(f"  - {sid}" for sid in ids) or "  （無）"
    return ListRegistrySkillsResult(
        success=True,
        message=f"skills/registry：\n{lines}",
        skill_ids=ids,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.LIST_REGISTRY_SKILLS,
        flow_id="list_registry_skills__work_flow",
        description_zh="find-skills：列出 registry skill",
        runner=run,
    )
