"""沙盒 subprocess 與 ToolPolicy。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from ai_company.modules.sandbox_runner.internal.tool_policy import (
    ToolPolicyError,
    is_high_risk_git,
    project_sandbox_root,
    validate_git_argv,
)


@dataclass(frozen=True)
class GitRunResult:
    returncode: int
    stdout: str
    stderr: str


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


__all__ = ["GitRunResult", "ToolPolicyError", "is_high_risk_git", "run_git_in_project_sandbox"]
