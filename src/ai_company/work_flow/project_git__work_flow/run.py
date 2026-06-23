from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.sandbox_runner.core import ToolPolicyError, run_git_in_project_sandbox
from ai_company.schemas.commands import BaseCommand, CommandType, ProjectGitCommand
from ai_company.schemas.results import ProjectGitResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ProjectGitResult:
    if not isinstance(command, ProjectGitCommand):
        return ProjectGitResult(success=False, message="指令類型錯誤", error_code="bad_command")
    try:
        project_id = require_active_project_id(deps.workspace_root, command.project_id)
    except ValueError as exc:
        return ProjectGitResult(success=False, message=str(exc), error_code="no_project")
    try:
        outcome = run_git_in_project_sandbox(
            deps.workspace_root,
            project_id,
            list(command.git_argv),
        )
    except ToolPolicyError as exc:
        return ProjectGitResult(
            success=False,
            message=str(exc),
            error_code="tool_policy",
            project_id=project_id,
        )
    combined = outcome.stdout.strip()
    if outcome.stderr.strip():
        detail = outcome.stderr.strip()
        combined = f"{combined}\n{detail}".strip() if combined else detail
    ok = outcome.returncode == 0
    return ProjectGitResult(
        success=ok,
        message=combined or f"git 結束碼 {outcome.returncode}",
        error_code=None if ok else "git_failed",
        project_id=project_id,
        exit_code=outcome.returncode,
        stdout=outcome.stdout,
        stderr=outcome.stderr,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.PROJECT_GIT,
        flow_id="project_git__work_flow",
        description_zh="PM 專案沙盒 Git（ToolPolicy 預檢）",
        runner=run,
    )
