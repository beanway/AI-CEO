#!/usr/bin/env python3
"""測試 GitHub CLI 與「建專案 → git init / gh repo create」整合。

前置：brew install gh && gh auth login（或 GH_TOKEN）

用法（在 repo 根目錄）：
  .venv/bin/python scripts/test_github_project_repo.py
      檢查 gh／.env，並在暫存工作區測本機 git init（不建遠端）

  .venv/bin/python scripts/test_github_project_repo.py --remote
      依 .env 的 GITHUB_* 在 GitHub 建立真實測試倉（專案名 GH-Integration-Test）

  .venv/bin/python scripts/test_github_project_repo.py --remote --delete-repo
      同上，結束後刪除遠端倉庫（本機暫存目錄仍會刪除）
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _fail(msg: str) -> int:
    print(f"  ✗ {msg}", file=sys.stderr)
    return 1


def check_gh() -> tuple[bool, str]:
    if not shutil.which("gh"):
        return False, "找不到 gh，請執行：brew install gh"
    proc = _run(["gh", "auth", "status"])
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return False, f"gh auth 未就緒：\n{out.strip()}"
    return True, out.strip()


def resolve_owner(settings) -> str:
    owner = settings.github_owner.strip()
    if owner:
        return owner
    proc = _run(["gh", "api", "user", "-q", ".login"])
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return ""


def parse_remote_repo_from_note(note: str) -> str | None:
    m = re.search(r"GitHub：已建立\s+([\w.-]+/[\w.-]+)\s", note)
    return m.group(1) if m else None


def main() -> int:
    parser = argparse.ArgumentParser(description="測試 gh 與專案 Git  bootstrap")
    parser.add_argument(
        "--remote",
        action="store_true",
        help="依 .env 呼叫 gh repo create（會在 GitHub 建立真實倉庫）",
    )
    parser.add_argument(
        "--delete-repo",
        action="store_true",
        help="與 --remote 合用：測試成功後 gh repo delete",
    )
    args = parser.parse_args()

    print("GitHub / 專案倉整合測試")
    print("─" * 40)

    ok, detail = check_gh()
    if not ok:
        return _fail(detail)
    _ok("gh 已安裝且已登入")
    for line in detail.splitlines()[:6]:
        print(f"    {line}")

    if not shutil.which("git"):
        return _fail("找不到 git")

    from ai_company.config import get_settings
    from ai_company.app_deps import AppDeps
    from ai_company.adapters.dispatch import dispatch
    from ai_company.schemas.commands import CreateProjectCommand, InitWorkspaceCommand
    import ai_company.work_flow._register  # noqa: F401

    settings = get_settings()
    owner = resolve_owner(settings)
    if owner:
        _ok(f"GitHub owner：{owner}")
    else:
        print("  ! 未設定 GITHUB_OWNER，且無法從 gh api 取得 login")

    auto = settings.github_auto_create_repo
    vis = settings.github_repo_visibility.strip() or "private"
    print(f"  .env  GITHUB_AUTO_CREATE_REPO={auto}")
    print(f"  .env  GITHUB_REPO_VISIBILITY={vis}")

    if args.remote:
        if not auto:
            return _fail("要建立遠端請在 .env 設 GITHUB_AUTO_CREATE_REPO=true")
        if not owner:
            return _fail("請設 GITHUB_OWNER=你的帳號或組織，或確保 gh api user 可用")
    else:
        print("\n（略過遠端：未加 --remote；僅測本機 git init）")

    parent = ROOT / "company_workspace"
    parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="ai-ceo-gh-test-", dir=parent))
    print(f"\n暫存工作區：{workspace}")

    test_settings = settings.model_copy(
        update={
            "company_workspace_root": workspace,
            "github_auto_create_repo": bool(args.remote and auto),
            "github_owner": owner or settings.github_owner,
        }
    )
    deps = AppDeps(settings=test_settings)

    init = dispatch(InitWorkspaceCommand(), deps)
    if not init.success:
        shutil.rmtree(workspace, ignore_errors=True)
        return _fail(f"init-workspace：{init.message}")
    _ok("init-workspace")

    created = dispatch(CreateProjectCommand(name="GH-Integration-Test"), deps)
    if not created.success or not created.project_id:
        shutil.rmtree(workspace, ignore_errors=True)
        return _fail(f"create_project：{created.message}")

    pid = created.project_id
    project_root = workspace / "projects" / pid
    print(f"\n{created.message}")

    if not (project_root / ".git").is_dir():
        shutil.rmtree(workspace, ignore_errors=True)
        return _fail("專案目錄缺少 .git")
    _ok("本機 .git 存在")

    remote_proc = _run(["git", "remote", "-v"], cwd=project_root)
    if remote_proc.stdout.strip():
        _ok(f"git remote：\n{remote_proc.stdout.strip()}")

    full_name = parse_remote_repo_from_note(created.message or "")
    if args.remote and not full_name:
        origin = _run(["git", "remote", "get-url", "origin"], cwd=project_root)
        if origin.returncode == 0:
            url = origin.stdout.strip()
            m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
            if m:
                full_name = f"{m.group(1)}/{m.group(2)}"

    if args.remote and full_name:
        view = _run(["gh", "repo", "view", full_name, "--json", "url", "-q", ".url"])
        if view.returncode == 0 and view.stdout.strip():
            _ok(f"遠端可存取：{view.stdout.strip()}")
        else:
            shutil.rmtree(workspace, ignore_errors=True)
            return _fail(f"gh repo view {full_name} 失敗：{(view.stderr or view.stdout).strip()}")

    if args.delete_repo and full_name:
        print(f"\n刪除遠端測試倉：{full_name}")
        deleted = _run(["gh", "repo", "delete", full_name, "--yes"])
        if deleted.returncode != 0:
            print(f"  ! 刪除失敗：{(deleted.stderr or deleted.stdout).strip()}", file=sys.stderr)
        else:
            _ok("已刪除遠端倉庫")

    shutil.rmtree(workspace, ignore_errors=True)
    _ok("已清除暫存工作區")

    print("\n全部檢查通過。")
    if not args.remote:
        print("若要測真實 GitHub 建倉：在 .env 設好 GITHUB_* 後執行")
        print("  .venv/bin/python scripts/test_github_project_repo.py --remote --delete-repo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
