from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.schemas.commands import AddSkillToProjectCommand, BaseCommand, Channel, CommandType
from ai_company.schemas.documents import ApprovalKind, PendingApprovalRecord
from ai_company.schemas.results import AddSkillToProjectResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> AddSkillToProjectResult:
    if not isinstance(command, AddSkillToProjectCommand):
        return AddSkillToProjectResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    skill_id = command.skill_id.strip()
    if not skill_registry.skill_exists(skill_id):
        return AddSkillToProjectResult(
            success=False,
            message=f"找不到 registry skill：{skill_id!r}",
            error_code="skill_not_found",
        )
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return AddSkillToProjectResult(
            success=False, message=str(exc), error_code="no_project"
        )
    if command.channel == Channel.TELEGRAM:
        record = file_store.create_pending_approval(
            deps.workspace_root,
            record=PendingApprovalRecord(
                id="_",
                kind=ApprovalKind.ADD_SKILL_TO_PROJECT,
                project_id=project_id,
                channel=command.channel.value,
                skill_id=skill_id,
                requester_telegram_id=command.telegram_user_id,
            ),
        )
        return AddSkillToProjectResult(
            success=False,
            message=f"專案 skill 安裝待核准（id={record.id}）",
            error_code="approval_required",
            project_id=project_id,
            skill_id=skill_id,
            approval_id=record.id,
        )
    data = file_store.load_project_skills(deps.workspace_root, project_id)
    if skill_id not in data.enabled_skill_ids:
        data.enabled_skill_ids.append(skill_id)
        file_store.save_project_skills(deps.workspace_root, project_id, data)
    return AddSkillToProjectResult(
        success=True,
        message=f"專案 {project_id} 已啟用 skill：{skill_id}",
        project_id=project_id,
        skill_id=skill_id,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.ADD_SKILL_TO_PROJECT,
        flow_id="add_skill_to_project__work_flow",
        description_zh="PM 啟用專案 project_skills.yaml",
        runner=run,
    )
