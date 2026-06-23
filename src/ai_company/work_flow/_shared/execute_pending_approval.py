"""核准後執行 pending approval 內容。"""

from __future__ import annotations

from dataclasses import dataclass

from ai_company.app_deps import AppDeps
from ai_company.modules.file_store import core as file_store
from ai_company.modules.sandbox_runner.core import ToolPolicyError, run_git_in_project_sandbox
from ai_company.modules.skill_registry import core as skill_registry
from ai_company.schemas.documents import ApprovalKind, PendingApprovalRecord


@dataclass(frozen=True)
class ExecutedApproval:
    message: str
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None


def execute_pending_approval(record: PendingApprovalRecord, deps: AppDeps) -> ExecutedApproval:
    if record.kind == ApprovalKind.PROJECT_GIT:
        argv = record.git_argv or []
        try:
            outcome = run_git_in_project_sandbox(deps.workspace_root, record.project_id, argv)
        except ToolPolicyError as exc:
            return ExecutedApproval(message=str(exc))
        combined = outcome.stdout.strip()
        if outcome.stderr.strip():
            detail = outcome.stderr.strip()
            combined = f"{combined}\n{detail}".strip() if combined else detail
        return ExecutedApproval(
            message=combined or f"git 結束碼 {outcome.returncode}",
            stdout=outcome.stdout,
            stderr=outcome.stderr,
            exit_code=outcome.returncode,
        )
    if record.kind == ApprovalKind.ADD_SKILL_TO_PROJECT:
        skill_id = (record.skill_id or "").strip()
        if not skill_registry.skill_exists(skill_id):
            return ExecutedApproval(message=f"找不到 registry skill：{skill_id!r}")
        data = file_store.load_project_skills(deps.workspace_root, record.project_id)
        if skill_id not in data.enabled_skill_ids:
            data.enabled_skill_ids.append(skill_id)
            file_store.save_project_skills(deps.workspace_root, record.project_id, data)
        return ExecutedApproval(
            message=f"專案 {record.project_id} 已啟用 skill：{skill_id}",
        )
    return ExecutedApproval(message=f"未知的核准類型：{record.kind}")
