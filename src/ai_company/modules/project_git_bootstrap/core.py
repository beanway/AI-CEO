"""建專案殼後的本機 Git 與可選 GitHub 遠端（gh CLI）。"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from ai_company.modules.settings.core import AppSettings

_PROJECT_GITIGNORE = """\
# Harness step markers
workers/*/.harness_step_done
"""


def slug_repo_name(project_name: str, project_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")[:40]
    if slug:
        return f"{slug}-{project_id}"
    return project_id


def bootstrap_project_git(
    project_root: Path,
    *,
    project_id: str,
    project_name: str,
    settings: AppSettings,
) -> str:
    """本機 git init；若設定開啟且已安裝 gh，則建立 GitHub 遠端倉庫。"""
    lines: list[str] = []
    if not shutil.which("git"):
        return "Git：未安裝 git，略過本機倉庫。"

    try:
        _ensure_local_git(project_root)
        lines.append("Git：已在本機 git init。")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        return f"Git：本機 init 失敗（{detail}）。"

    if not settings.github_auto_create_repo:
        return "\n".join(lines)

    owner = settings.github_owner.strip()
    if not owner:
        lines.append("GitHub：已啟用 GITHUB_AUTO_CREATE_REPO 但未設定 GITHUB_OWNER，略過遠端。")
        return "\n".join(lines)

    if not shutil.which("gh"):
        lines.append("GitHub：未安裝 gh CLI，略過遠端（請 brew install gh && gh auth login）。")
        return "\n".join(lines)

    repo = slug_repo_name(project_name, project_id)
    full_name = f"{owner}/{repo}"
    visibility = settings.github_repo_visibility.strip().lower()
    if visibility not in ("public", "private"):
        visibility = "private"

    if (project_root / ".git" / "config").is_file():
        try:
            existing = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if existing.returncode == 0 and existing.stdout.strip():
                lines.append(f"GitHub：已有 origin，略過建立（{existing.stdout.strip()}）。")
                return "\n".join(lines)
        except OSError:
            pass

    cmd = [
        "gh",
        "repo",
        "create",
        full_name,
        f"--{visibility}",
        "--source=.",
        "--remote=origin",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        lines.append(f"GitHub：執行 gh 失敗（{exc}）。")
        return "\n".join(lines)

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()
        lines.append(f"GitHub：建立遠端失敗（{err}）。")
        return "\n".join(lines)

    lines.append(f"GitHub：已建立 {full_name} 並設定 origin。")
    return "\n".join(lines)


def _ensure_local_git(project_root: Path) -> None:
    git_dir = project_root / ".git"
    if not git_dir.exists():
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(_PROJECT_GITIGNORE, encoding="utf-8")
