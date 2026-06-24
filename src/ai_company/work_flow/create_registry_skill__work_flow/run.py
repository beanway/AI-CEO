from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.schemas.commands import BaseCommand, CommandType, CreateRegistrySkillCommand
from ai_company.schemas.results import CreateRegistrySkillResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> CreateRegistrySkillResult:
    del deps
    if not isinstance(command, CreateRegistrySkillCommand):
        return CreateRegistrySkillResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    skill_id = command.skill_id.strip()
    if skill_registry.skill_exists(skill_id):
        return CreateRegistrySkillResult(
            success=False,
            message=f"skill 已存在：{skill_id}",
            error_code="exists",
            skill_id=skill_id,
        )
    try:
        path = skill_registry.create_registry_skill_stub(
            skill_id, description=command.description
        )
    except ValueError as exc:
        return CreateRegistrySkillResult(
            success=False, message=str(exc), error_code="invalid_skill_id"
        )
    except FileExistsError:
        return CreateRegistrySkillResult(
            success=False,
            message=f"目錄已存在：{skill_id}",
            error_code="exists",
            skill_id=skill_id,
        )
    return CreateRegistrySkillResult(
        success=True,
        message=f"已建立 registry skill：{skill_id}",
        skill_id=skill_id,
        path=str(path),
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.CREATE_REGISTRY_SKILL,
        flow_id="create_registry_skill__work_flow",
        description_zh="create-skill：建立 registry stub",
        runner=run,
    )
