"""沙盒 subprocess 與 ToolPolicy。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ai_company.modules.sandbox_runner.internal.backend_tool_policy import (
    validate_backend_argv,
    validate_backend_relative_path,
)
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
    validate_backend_argv(argv)
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


def read_file_in_backend_sandbox(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    rel_path: str,
) -> str:
    path = validate_backend_relative_path(
        workspace_root, project_id, worker_id, rel_path, for_write=False
    )
    if not path.is_file():
        raise ToolPolicyError(f"檔案不存在：{rel_path!r}")
    return path.read_text(encoding="utf-8")


def write_file_in_backend_sandbox(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    rel_path: str,
    content: str,
) -> None:
    path = validate_backend_relative_path(
        workspace_root, project_id, worker_id, rel_path, for_write=True
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def complete_worker_harness_step(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> WorkerStepResult:
    """在 workers/<id>/ 寫入步驟完成標記；subprocess cwd 為專案根。"""
    project_root = worker_sandbox_cwd(workspace_root, project_id, worker_id)
    marker = project_root / "workers" / worker_id / ".harness_step_done"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
    return WorkerStepResult(
        worker_id=worker_id,
        marker_path=str(marker.relative_to(project_root)),
    )


__all__ = [
    "GitRunResult",
    "SubprocessRunResult",
    "ToolPolicyError",
    "WorkerStepResult",
    "complete_worker_harness_step",
    "is_high_risk_git",
    "read_file_in_backend_sandbox",
    "run_argv_in_worker_cwd",
    "run_git_in_project_sandbox",
    "write_file_in_backend_sandbox",
]
