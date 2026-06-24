from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.work_flow._shared.company_workspace import ensure_company_workspace
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.schemas.commands import (
    AddSkillToCompanyCommand,
    BaseCommand,
    CommandType,
)
from ai_company.schemas.documents import GlobalSkillsFile
from ai_company.schemas.results import AddSkillToCompanyResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> AddSkillToCompanyResult:
    if not isinstance(command, AddSkillToCompanyCommand):
        return AddSkillToCompanyResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    skill_id = command.skill_id.strip()
    if not skill_id:
        return AddSkillToCompanyResult(
            success=False,
            message="skill id 不可為空白",
            error_code="invalid_skill_id",
        )
    if not skill_registry.skill_exists(skill_id):
        known = ", ".join(skill_registry.list_registered_skill_ids()) or "（無）"
        return AddSkillToCompanyResult(
            success=False,
            message=f"registry 找不到 skill {skill_id!r}。可用：{known}",
            error_code="skill_not_found",
        )
    ensure_company_workspace(deps.workspace_root)
    skills = file_store.load_global_skills(deps.workspace_root)
    if skill_id in skills.enabled_skill_ids:
        return AddSkillToCompanyResult(
            success=True,
            message=f"skill 已在全公司啟用：{skill_id}",
            skill_id=skill_id,
        )
    skills = GlobalSkillsFile(enabled_skill_ids=[*skills.enabled_skill_ids, skill_id])
    file_store.save_global_skills(deps.workspace_root, skills)
    return AddSkillToCompanyResult(
        success=True,
        message=f"已啟用全公司 skill → {skill_id}",
        skill_id=skill_id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.ADD_SKILL_TO_COMPANY,
        flow_id="add_skill_to_company__work_flow",
        description_zh="CEO 啟用 global_skills registry skill",
        runner=run,
    )
