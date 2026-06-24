"""Git 與路徑的 ToolPolicy 預檢（僅專案沙盒）。"""

from __future__ import annotations

from pathlib import Path

from ai_company.schemas.workspace_paths import project_dir

_PATH_FLAGS = frozenset(
    {
        "-C",
        "--git-dir",
        "--work-tree",
        "--namespace",
    }
)


class ToolPolicyError(ValueError):
    """工具政策拒絕執行。"""


def project_sandbox_root(workspace_root: Path, project_id: str) -> Path:
    root = project_dir(workspace_root, project_id)
    if not root.is_dir():
        raise ToolPolicyError(f"專案目錄不存在：{project_id!r}")
    return root.resolve()


def worker_sandbox_cwd(workspace_root: Path, project_id: str, worker_id: str) -> Path:
    """Worker subprocess 的 cwd：projects/<id>/ 根（須已存在 workers/<worker_id>/）。"""
    root = project_sandbox_root(workspace_root, project_id)
    worker_dir = (root / "workers" / worker_id).resolve()
    if not worker_dir.is_dir():
        raise ToolPolicyError(f"Worker 目錄不存在：workers/{worker_id}/")
    if not _path_within_root(worker_dir, root):
        raise ToolPolicyError(f"Worker 目錄超出沙盒：{worker_id!r}")
    return root


def _path_within_root(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _resolve_git_path(raw: str, *, cwd: Path, root: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = (cwd / path).resolve()
    else:
        path = path.resolve()
    if not _path_within_root(path, root):
        raise ToolPolicyError(f"Git 路徑超出專案沙盒：{raw!r}")
    return path


def validate_git_argv(workspace_root: Path, project_id: str, git_argv: list[str]) -> None:
    """驗證 git 子命令與 -C/--git-dir 等路徑皆限於 projects/<id>/。"""
    if not git_argv:
        raise ToolPolicyError("git 至少需要一個子命令")
    root = project_sandbox_root(workspace_root, project_id)
    cwd = root
    i = 0
    while i < len(git_argv):
        token = git_argv[i]
        if token in _PATH_FLAGS:
            if i + 1 >= len(git_argv):
                raise ToolPolicyError(f"缺少 {token} 的路徑參數")
            raw_path = git_argv[i + 1]
            resolved = _resolve_git_path(raw_path, cwd=cwd, root=root)
            if token in ("-C", "--git-dir", "--work-tree"):
                cwd = resolved if token == "-C" else cwd
            i += 2
            continue
        if token.startswith("--git-dir="):
            raw_path = token.split("=", 1)[1]
            _resolve_git_path(raw_path, cwd=cwd, root=root)
            i += 1
            continue
        if token.startswith("--work-tree="):
            raw_path = token.split("=", 1)[1]
            _resolve_git_path(raw_path, cwd=cwd, root=root)
            i += 1
            continue
        if token == "--":
            break
        if token.startswith("-"):
            i += 1
            continue
        break
    subcommand = git_argv[i]
    if subcommand.startswith("-"):
        raise ToolPolicyError("無法解析 git 子命令")
    forbidden = {"config", "daemon", "upload-pack", "receive-pack"}
    if subcommand in forbidden:
        raise ToolPolicyError(f"git {subcommand} 不允許在 PM 沙盒執行")


def is_high_risk_git(git_argv: list[str]) -> bool:
    """高風險 git 子命令（需 TG 核准後才可執行）。"""
    if not git_argv:
        return True
    i = 0
    while i < len(git_argv) and git_argv[i].startswith("-"):
        if git_argv[i] in _PATH_FLAGS and i + 1 < len(git_argv):
            i += 2
            continue
        if git_argv[i] == "--":
            i += 1
            break
        i += 1
    if i >= len(git_argv):
        return True
    sub = git_argv[i].lower()
    high = {
        "commit",
        "push",
        "pull",
        "merge",
        "rebase",
        "reset",
        "clean",
        "checkout",
        "switch",
        "restore",
        "revert",
        "cherry-pick",
        "rm",
        "mv",
        "stash",
        "tag",
        "fetch",
        "clone",
        "submodule",
        "worktree",
    }
    return sub in high
