"""沙盒 subprocess 與 ToolPolicy。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ai_company.modules.sandbox_runner.internal.tool_policy import (
    ToolPolicyError,
    is_high_risk_git,
    project_sandbox_root,
    validate_git_argv,
    worker_sandbox_cwd,
)


@dataclass(frozen=True)
class GitRunResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class SubprocessRunResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class WorkerStepResult:
    worker_id: str
    marker_path: str


def run_git_in_project_sandbox(
    workspace_root: Path,
    project_id: str,
    git_argv: list[str],
) -> GitRunResult:
    validate_git_argv(workspace_root, project_id, git_argv)
    root = project_sandbox_root(workspace_root, project_id)
    proc = subprocess.run(
        ["git", *git_argv],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return GitRunResult(
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )


def run_argv_in_worker_cwd(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    argv: list[str],
) -> SubprocessRunResult:
    if not argv:
        raise ToolPolicyError("argv 不可為空")
    cwd = worker_sandbox_cwd(workspace_root, project_id, worker_id)
    proc = subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return SubprocessRunResult(
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )


def complete_worker_harness_step(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> WorkerStepResult:
    """在 Worker cwd 寫入步驟完成標記（Phase B 沙盒執行最小產物）。"""
    cwd = worker_sandbox_cwd(workspace_root, project_id, worker_id)
    marker = cwd / ".harness_step_done"
    marker.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
    return WorkerStepResult(worker_id=worker_id, marker_path=str(marker.relative_to(cwd)))


__all__ = [
    "GitRunResult",
    "SubprocessRunResult",
    "ToolPolicyError",
    "WorkerStepResult",
    "complete_worker_harness_step",
    "is_high_risk_git",
    "run_argv_in_worker_cwd",
    "run_git_in_project_sandbox",
]
