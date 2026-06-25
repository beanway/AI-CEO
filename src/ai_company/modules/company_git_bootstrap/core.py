"""company_workspace/_company 本機 Git 與 GitHub 遠端（廣域設定倉）。"""

from __future__ import annotations

import shutil
from pathlib import Path

from ai_company.modules.file_store import core as file_store
from ai_company.modules.project_git_bootstrap import github_common as gh
from ai_company.modules.settings.core import AppSettings

DEFAULT_COMPANY_REPO_NAME = "ai-ceo-company"
COMPANY_DIR = "_company"


def company_dir(workspace_root: Path) -> Path:
    return workspace_root / COMPANY_DIR


def bootstrap_company_github(
    workspace_root: Path,
    settings: AppSettings,
    *,
    create_remote: bool,
    push: bool = True,
) -> str:
    """在 workspace/_company 初始化 git；可選 gh 建立遠端並 push（僅含 .gitignore 允許的設定檔）。"""
    root = company_dir(workspace_root)
    if not root.is_dir():
        return f"_company 目錄不存在：{root}"

    lines: list[str] = []
    if not shutil.which("git"):
        return "Git：未安裝 git。"

    try:
        gh.git_init_with_gitignore(root, file_store.COMPANY_GITIGNORE_TEXT)
        lines.append("Git：已更新 .gitignore 並確保本機倉庫。")
    except Exception as exc:
        return f"Git：init 失敗（{exc}）。"

    try:
        if gh.ensure_initial_commit(root, message="chore: company settings baseline"):
            lines.append("Git：已建立初始 commit（僅廣域設定檔）。")
        else:
            lines.append("Git：已有 commit，略過初始提交。")
    except Exception as exc:
        return f"Git：commit 失敗（{exc}）。"

    if not create_remote:
        return "\n".join(lines)

    owner = settings.github_owner.strip()
    if not owner:
        lines.append("GitHub：未設定 GITHUB_OWNER，略過遠端。")
        return "\n".join(lines)

    existing = gh.has_origin(root)
    repo_name = (settings.github_company_repo_name or DEFAULT_COMPANY_REPO_NAME).strip()
    if not repo_name:
        repo_name = DEFAULT_COMPANY_REPO_NAME
    full_name = f"{owner}/{repo_name}"

    if existing:
        lines.append(f"GitHub：已有 origin（{existing}）。")
        if push:
            push_out = gh.git_push_origin(root, full_name)
            if push_out.ok:
                lines.append("GitHub：已 push 目前分支。")
            else:
                lines.append(f"GitHub：push 失敗（{push_out.message}）。")
        return "\n".join(lines)

    visibility = gh.resolve_visibility(settings)

    outcome = gh.gh_repo_create_from_source(
        root,
        full_name,
        visibility,
        push=push,
    )
    if not outcome.ok:
        lines.append(f"GitHub：建立遠端失敗（{outcome.message}）。")
        return "\n".join(lines)

    lines.append(f"GitHub：已建立 {outcome.message} 並設定 origin。")
    if push:
        lines.append("GitHub：已 push 目前分支（不含 sessions／execution 等）。")
    return "\n".join(lines)
