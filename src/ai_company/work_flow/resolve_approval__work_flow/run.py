from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import BaseCommand, CommandType, ResolveApprovalCommand
from ai_company.schemas.documents import ApprovalStatus
from ai_company.schemas.results import ResolveApprovalResult
from ai_company.work_flow._shared.execute_pending_approval import execute_pending_approval
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ResolveApprovalResult:
    if not isinstance(command, ResolveApprovalCommand):
        return ResolveApprovalResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    record = file_store.get_pending_approval(deps.workspace_root, command.approval_id)
    if record is None:
        return ResolveApprovalResult(
            success=False,
            message=f"找不到核准請求：{command.approval_id!r}",
            error_code="not_found",
        )
    if record.status != ApprovalStatus.PENDING:
        return ResolveApprovalResult(
            success=False,
            message=f"核准請求已處理（{record.status.value}）",
            error_code="already_resolved",
            approval_id=record.id,
        )
    if not command.approved:
        rejected = record.model_copy(update={"status": ApprovalStatus.REJECTED})
        file_store.update_pending_approval(deps.workspace_root, rejected)
        return ResolveApprovalResult(
            success=True,
            message=f"已拒絕核准 {record.id}",
            approval_id=record.id,
            approved=False,
        )
    outcome = execute_pending_approval(record, deps)
    ok = outcome.exit_code in (None, 0)
    completed = record.model_copy(update={"status": ApprovalStatus.COMPLETED})
    file_store.update_pending_approval(deps.workspace_root, completed)
    return ResolveApprovalResult(
        success=ok,
        message=outcome.message,
        error_code=None if ok else "execution_failed",
        approval_id=record.id,
        approved=True,
        exit_code=outcome.exit_code,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.RESOLVE_APPROVAL,
        flow_id="resolve_approval__work_flow",
        description_zh="處理 TG Inline 核准／拒絕",
        runner=run,
    )
