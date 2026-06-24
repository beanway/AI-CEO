"""本機 git 與 gh repo create 共用邏輯。"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ai_company.modules.settings.core import AppSettings


@dataclass(frozen=True)
class GhCreateOutcome:
    ok: bool
    message: str


def resolve_visibility(settings: AppSettings) -> str:
    visibility = settings.github_repo_visibility.strip().lower()
    if visibility not in ("public", "private"):
        return "private"
    return visibility


def git_init_with_gitignore(repo_root: Path, gitignore_text: str) -> None:
    if not (repo_root / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    (repo_root / ".gitignore").write_text(gitignore_text, encoding="utf-8")


def has_origin(repo_root: Path) -> str | None:
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return None


def ensure_initial_commit(repo_root: Path, *, message: str) -> bool:
    """若尚無 commit，git add -A（受 .gitignore）並提交。回傳是否新建了 commit。"""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if head.returncode == 0:
        return False
    subprocess.run(
        ["git", "add", "-A"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode == 0:
        return False
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return True


def gh_repo_create_from_source(
    repo_root: Path,
    full_name: str,
    visibility: str,
    *,
    push: bool,
) -> GhCreateOutcome:
    if not shutil.which("gh"):
        return GhCreateOutcome(ok=False, message="未安裝 gh CLI")
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
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return GhCreateOutcome(ok=False, message=str(exc))
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()
        if "already exists" not in err.lower():
            return GhCreateOutcome(ok=False, message=err)
        if gh.has_origin(repo_root) is None:
            _set_origin_https(repo_root, full_name)

    if push:
        push_out = git_push_origin(repo_root, full_name)
        if not push_out.ok:
            return push_out
    return GhCreateOutcome(ok=True, message=full_name)


def _set_origin_https(repo_root: Path, full_name: str) -> None:
    proc = subprocess.run(
        ["gh", "repo", "view", full_name, "--json", "url", "-q", ".url"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return
    url = proc.stdout.strip()
    if not url.endswith(".git"):
        url = f"{url}.git"
    subprocess.run(
        ["git", "remote", "set-url", "origin", url],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


def git_push_origin(repo_root: Path, full_name: str) -> GhCreateOutcome:
    subprocess.run(
        ["gh", "auth", "setup-git"],
        capture_output=True,
        text=True,
        check=False,
    )
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    br = (branch.stdout or "").strip() or "main"
    proc = subprocess.run(
        ["git", "push", "-u", "origin", br],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return GhCreateOutcome(ok=True, message=full_name)
    _set_origin_https(repo_root, full_name)
    proc = subprocess.run(
        ["git", "push", "-u", "origin", br],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        return GhCreateOutcome(ok=False, message=err)
    return GhCreateOutcome(ok=True, message=full_name)
