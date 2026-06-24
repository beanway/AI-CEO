from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.work_flow._shared.company_workspace import ensure_company_workspace
from ai_company.schemas.commands import (
    BaseCommand,
    CommandType,
    RemoveSkillFromCompanyCommand,
)
from ai_company.schemas.documents import GlobalSkillsFile
from ai_company.schemas.results import RemoveSkillFromCompanyResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> RemoveSkillFromCompanyResult:
    if not isinstance(command, RemoveSkillFromCompanyCommand):
        return RemoveSkillFromCompanyResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    skill_id = command.skill_id.strip()
    if not skill_id:
        return RemoveSkillFromCompanyResult(
            success=False,
            message="skill id 不可為空白",
            error_code="invalid_skill_id",
        )
    ensure_company_workspace(deps.workspace_root)
    skills = file_store.load_global_skills(deps.workspace_root)
    if skill_id not in skills.enabled_skill_ids:
        return RemoveSkillFromCompanyResult(
            success=True,
            message=f"skill 未在全公司啟用：{skill_id}",
            skill_id=skill_id,
        )
    remaining = [s for s in skills.enabled_skill_ids if s != skill_id]
    file_store.save_global_skills(
        deps.workspace_root,
        GlobalSkillsFile(enabled_skill_ids=remaining),
    )
    return RemoveSkillFromCompanyResult(
        success=True,
        message=f"已從全公司停用 skill → {skill_id}",
        skill_id=skill_id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.REMOVE_SKILL_FROM_COMPANY,
        flow_id="remove_skill_from_company__work_flow",
        description_zh="CEO 停用 global_skills registry skill",
        runner=run,
    )
