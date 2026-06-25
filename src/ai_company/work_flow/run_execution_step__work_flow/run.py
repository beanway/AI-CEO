from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.execution_store import core as execution_store
from ai_company.modules.file_store import core as file_store
from ai_company.modules.notify import core as notify
from ai_company.modules.sandbox_runner.core import (
    ToolPolicyError,
    complete_worker_harness_step,
)
from ai_company.modules.worker_host import core as worker_host
from ai_company.modules.metrics import core as metrics
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.modules.task_scheduler import core as task_scheduler
from ai_company.modules.task_scoring import core as task_scoring
from ai_company.schemas.commands import BaseCommand, CommandType, RunExecutionStepCommand
from ai_company.schemas.documents import (
    ApprovalStatus,
    ExecutionStateFile,
    ExecutionStatus,
    PendingExecutionFailureRecord,
    ProjectLifecycle,
)
from ai_company.schemas.results import RunExecutionStepResult
from ai_company.schemas.workspace_paths import project_dir
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def _notify_progress(
    deps: AppDeps,
    *,
    project_id: str,
    worker_id: str,
    text: str,
    failed: bool,
) -> None:
    cfg = file_store.load_global_config(deps.workspace_root)
    if not notify.should_notify(cfg.notification_policy, failed=failed):
        return
    chat_id = cfg.executor_notify_chat_id
    if chat_id is None:
        return
    notify.send_executor_message(
        chat_id,
        f"[project={project_id}] worker={worker_id}\n{text}",
    )


def _resolve_worker_id(
    workspace_root,
    project_id: str,
) -> tuple[str | None, bool]:
    """回傳 (worker_id, from_queue)。"""
    peek = execution_store.peek_next_pending(workspace_root)
    if peek is not None and peek.project_id == project_id:
        return peek.worker_id, True
    workers = file_store.load_workers(workspace_root, project_id)
    harness = file_store.load_project_harness_state(workspace_root, project_id)
    worker_id, _ = task_scheduler.pick_next_worker(workers, harness)
    return worker_id, False


def run(command: BaseCommand, deps: AppDeps) -> RunExecutionStepResult:
    if not isinstance(command, RunExecutionStepCommand):
        return RunExecutionStepResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return RunExecutionStepResult(
            success=False, message=str(exc), error_code="no_project"
        )

    if execution_store.list_running_globally(deps.workspace_root):
        return RunExecutionStepResult(
            success=False,
            message="全公司已有進行中的 execution，請稍後再派工",
            error_code="busy",
            project_id=project_id,
        )

    pending_fail = file_store.pending_execution_failure_for_project(
        deps.workspace_root, project_id
    )
    if pending_fail is not None:
        return RunExecutionStepResult(
            success=False,
            message=f"專案有待處理失敗（failure_id={pending_fail.id}），請先 resolve",
            error_code="pending_failure",
            project_id=project_id,
            failure_id=pending_fail.id,
        )

    workers = file_store.load_workers(deps.workspace_root, project_id)
    if not workers.workers:
        return RunExecutionStepResult(
            success=False,
            message="尚未建局（workers.yaml 為空）",
            error_code="no_workers",
            project_id=project_id,
        )

    harness = file_store.load_project_harness_state(deps.workspace_root, project_id)
    if harness.lifecycle == ProjectLifecycle.PROJECT_DONE:
        return RunExecutionStepResult(
            success=True,
            message=f"專案 {project_id} 已 PROJECT_DONE",
            project_id=project_id,
            project_done=True,
        )

    worker_id, from_queue = _resolve_worker_id(deps.workspace_root, project_id)
    if worker_id is None:
        return RunExecutionStepResult(
            success=True,
            message=f"專案 {project_id} 無下一個 Worker（可能已完成）",
            project_id=project_id,
            project_done=True,
        )

    entry = task_scheduler.worker_entry_by_id(workers, worker_id)
    if entry is None:
        return RunExecutionStepResult(
            success=False,
            message=f"worker {worker_id!r} 不在編制中",
            error_code="invalid_worker",
            project_id=project_id,
        )

    global_config = file_store.load_global_config(deps.workspace_root)
    if (
        global_config.dispatch_min_score is not None
        and harness.last_completed_worker_id is not None
    ):
        ok_score, scored = task_scoring.passes_dispatch_gate(
            deps.workspace_root,
            project_id,
            previous_worker_id=harness.last_completed_worker_id,
            min_score=global_config.dispatch_min_score,
        )
        metrics.append_usage_event(
            deps.workspace_root,
            event="task_score",
            project_id=project_id,
            role=harness.last_completed_worker_id,
            tokens_estimated=0,
            detail=f"score={scored.value} reasons={','.join(scored.reasons)}",
        )
        file_store.append_scheduler_decision(
            deps.workspace_root,
            project_id,
            event="task_score",
            worker_id=harness.last_completed_worker_id,
            detail=f"score={scored.value} min={global_config.dispatch_min_score}",
        )
        if not ok_score:
            return RunExecutionStepResult(
                success=False,
                message=(
                    f"上一 Worker {harness.last_completed_worker_id} 評分 {scored.value} "
                    f"低於門檻 {global_config.dispatch_min_score}，拒絕派工"
                ),
                error_code="score_below_threshold",
                project_id=project_id,
                worker_id=worker_id,
            )

    if from_queue:
        dequeued = execution_store.dequeue_next_pending(deps.workspace_root)
        if dequeued is None or dequeued.worker_id != worker_id:
            return RunExecutionStepResult(
                success=False,
                message="佇列狀態不一致，請重試",
                error_code="queue_race",
                project_id=project_id,
            )

    execution_id = execution_store.new_execution_id()
    execution_store.save_execution_state(
        deps.workspace_root,
        ExecutionStateFile(
            execution_id=execution_id,
            project_id=project_id,
            worker_id=worker_id,
            status=ExecutionStatus.RUNNING,
        ),
    )

    stack = skill_registry.resolve_skill_stack(deps.workspace_root, project_id, worker_id)
    file_store.append_scheduler_decision(
        deps.workspace_root,
        project_id,
        event="dispatch",
        worker_id=worker_id,
        detail=f"skills={','.join(stack) or '-'}",
    )

    if command.simulate_failure:
        reason = "simulate_failure"
        execution_store.save_execution_state(
            deps.workspace_root,
            ExecutionStateFile(
                execution_id=execution_id,
                project_id=project_id,
                worker_id=worker_id,
                status=ExecutionStatus.FAILED,
                failure_reason=reason,
            ),
        )
        failure = file_store.create_pending_execution_failure(
            deps.workspace_root,
            record=PendingExecutionFailureRecord(
                id="pending",
                execution_id=execution_id,
                project_id=project_id,
                worker_id=worker_id,
                reason=reason,
            ),
        )
        file_store.append_scheduler_decision(
            deps.workspace_root,
            project_id,
            event="failed",
            worker_id=worker_id,
            detail=reason,
        )
        _notify_progress(
            deps,
            project_id=project_id,
            worker_id=worker_id,
            text=f"失敗：{reason}（failure_id={failure.id}）",
            failed=True,
        )
        return RunExecutionStepResult(
            success=False,
            message=f"Worker {worker_id} 失敗：{reason}；請 TG 選 retry / code_review",
            error_code="worker_failed",
            project_id=project_id,
            execution_id=execution_id,
            worker_id=worker_id,
            failure_id=failure.id,
        )

    try:
        if entry.kind == "backend" and worker_host.has_backend_task(
            deps.workspace_root, project_id
        ):
            host_result = worker_host.run_backend_execution_step(
                deps.workspace_root, project_id, worker_id
            )
            if not host_result.success:
                raise ToolPolicyError(host_result.error or host_result.summary)
        elif entry.kind == "task_scheduler" and worker_host.has_scheduler_intake(
            deps.workspace_root, project_id
        ):
            host_result = worker_host.run_scheduler_execution_step(
                deps.workspace_root, project_id, worker_id
            )
            if not host_result.success:
                raise ToolPolicyError(host_result.error or host_result.summary)
        step = complete_worker_harness_step(deps.workspace_root, project_id, worker_id)
    except ToolPolicyError as exc:
        reason = str(exc)
        execution_store.save_execution_state(
            deps.workspace_root,
            ExecutionStateFile(
                execution_id=execution_id,
                project_id=project_id,
                worker_id=worker_id,
                status=ExecutionStatus.FAILED,
                failure_reason=reason,
            ),
        )
        failure = file_store.create_pending_execution_failure(
            deps.workspace_root,
            record=PendingExecutionFailureRecord(
                id="pending",
                execution_id=execution_id,
                project_id=project_id,
                worker_id=worker_id,
                reason=reason,
            ),
        )
        file_store.append_scheduler_decision(
            deps.workspace_root,
            project_id,
            event="failed",
            worker_id=worker_id,
            detail=reason,
        )
        _notify_progress(
            deps,
            project_id=project_id,
            worker_id=worker_id,
            text=f"失敗：{reason}",
            failed=True,
        )
        return RunExecutionStepResult(
            success=False,
            message=reason,
            error_code="tool_policy",
            project_id=project_id,
            execution_id=execution_id,
            worker_id=worker_id,
            failure_id=failure.id,
        )

    if entry.kind == "qa":
        qa_out = project_dir(deps.workspace_root, project_id) / "shared" / "qa_passed.txt"
        qa_out.parent.mkdir(parents=True, exist_ok=True)
        qa_out.write_text("passed\n", encoding="utf-8")

    execution_store.save_execution_state(
        deps.workspace_root,
        ExecutionStateFile(
            execution_id=execution_id,
            project_id=project_id,
            worker_id=worker_id,
            status=ExecutionStatus.DONE,
        ),
    )

    harness = harness.model_copy(update={"last_completed_worker_id": worker_id})
    _, harness_after = task_scheduler.pick_next_worker(workers, harness)
    file_store.save_project_harness_state(deps.workspace_root, project_id, harness_after)

    project_done = harness_after.lifecycle == ProjectLifecycle.PROJECT_DONE
    if project_done:
        file_store.set_project_lifecycle_done(deps.workspace_root, project_id)
        file_store.append_scheduler_decision(
            deps.workspace_root,
            project_id,
            event="project_done",
            worker_id=worker_id,
            detail="QA 閉環",
        )

    file_store.append_scheduler_decision(
        deps.workspace_root,
        project_id,
        event="completed",
        worker_id=worker_id,
        detail=step.marker_path,
    )
    _notify_progress(
        deps,
        project_id=project_id,
        worker_id=worker_id,
        text="完成" + (" · PROJECT_DONE" if project_done else ""),
        failed=False,
    )

    msg = f"Worker {worker_id} 完成（execution={execution_id}）"
    if project_done:
        msg += " · 專案 PROJECT_DONE"
    return RunExecutionStepResult(
        success=True,
        message=msg,
        project_id=project_id,
        execution_id=execution_id,
        worker_id=worker_id,
        project_done=project_done,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.RUN_EXECUTION_STEP,
        flow_id="run_execution_step__work_flow",
        description_zh="執行層：派工並跑一步 Worker（沙盒）",
        runner=run,
    )
