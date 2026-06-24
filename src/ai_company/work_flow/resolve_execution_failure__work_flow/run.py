from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.execution_store import core as execution_store
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import (
    BaseCommand,
    CommandType,
    ResolveExecutionFailureCommand,
)
from ai_company.schemas.documents import ApprovalStatus, ExecutionFailureDecision
from ai_company.schemas.results import ResolveExecutionFailureResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ResolveExecutionFailureResult:
    if not isinstance(command, ResolveExecutionFailureCommand):
        return ResolveExecutionFailureResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    record = file_store.get_pending_execution_failure(
        deps.workspace_root, command.failure_id
    )
    if record is None:
        return ResolveExecutionFailureResult(
            success=False,
            message=f"找不到 failure：{command.failure_id!r}",
            error_code="not_found",
        )
    if record.status != ApprovalStatus.PENDING:
        return ResolveExecutionFailureResult(
            success=False,
            message=f"failure 已處理（{record.status.value}）",
            error_code="already_resolved",
            failure_id=record.id,
        )

    decision = ExecutionFailureDecision(command.decision)
    workers = file_store.load_workers(deps.workspace_root, record.project_id)

    if decision == ExecutionFailureDecision.RETRY:
        execution_store.enqueue_dispatch(
            deps.workspace_root,
            project_id=record.project_id,
            worker_id=record.worker_id,
        )
        detail = f"retry worker={record.worker_id}"
    else:
        planner_id = None
        for entry in workers.workers:
            if entry.kind == "planner":
                planner_id = entry.id
                break
        target = planner_id or record.worker_id
        execution_store.enqueue_dispatch(
            deps.workspace_root,
            project_id=record.project_id,
            worker_id=target,
        )
        detail = f"code_review → enqueue {target}"

    file_store.append_scheduler_decision(
        deps.workspace_root,
        record.project_id,
        event="failure_decision",
        worker_id=record.worker_id,
        detail=detail,
    )

    completed = record.model_copy(
        update={"status": ApprovalStatus.COMPLETED, "decision": decision},
    )
    file_store.update_pending_execution_failure(deps.workspace_root, completed)

    return ResolveExecutionFailureResult(
        success=True,
        message=f"已記錄決策 {decision.value}：{detail}",
        failure_id=record.id,
        decision=decision.value,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.RESOLVE_EXECUTION_FAILURE,
        flow_id="resolve_execution_failure__work_flow",
        description_zh="執行失敗：重試或 code review",
        runner=run,
    )
