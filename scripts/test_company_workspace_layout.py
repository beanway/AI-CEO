#!/usr/bin/env python3
"""驗證 Harness 公司沙盒路徑是否正確（_company、projects 應在 COMPANY_WORKSPACE_ROOT 下）。

用法（在 repo 根目錄）：
  .venv/bin/python scripts/test_company_workspace_layout.py

選項：
  --smoke-create   在暫存工作區建立測試專案殼後刪除（不動本機 company_workspace）
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _fail(msg: str) -> int:
    print(f"  ✗ {msg}", file=sys.stderr)
    return 1


def _warn(msg: str) -> None:
    print(f"  ! {msg}")


def check_no_legacy_repo_root_dirs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    legacy_company = repo_root / "_company"
    legacy_projects = repo_root / "projects"
    if legacy_company.is_dir():
        remaining = [p.name for p in legacy_company.iterdir() if p.name != "MIGRATED.txt"]
        if remaining:
            errors.append(
                f"repo 根仍有 _company/（應僅在 company_workspace 下）：{remaining[:5]}"
            )
        else:
            _warn("repo 根 _company/ 僅剩 MIGRATED.txt，可手動刪除該目錄")
    if legacy_projects.is_dir() and any(legacy_projects.iterdir()):
        errors.append("repo 根仍有 projects/<id>/，應在 company_workspace/projects/ 下")
    return errors


def check_workspace_layout(workspace: Path) -> list[str]:
    errors: list[str] = []
    company = workspace / "_company"
    projects = workspace / "projects"
    if not workspace.is_dir():
        errors.append(f"工作區不存在：{workspace}")
        return errors
    if not company.is_dir():
        errors.append(f"缺少 {workspace.name}/_company/")
    if not projects.is_dir():
        errors.append(f"缺少 {workspace.name}/projects/")
    projects_json = company / "projects.json"
    if company.is_dir() and not projects_json.is_file():
        errors.append(f"缺少 {workspace.name}/_company/projects.json")
    return errors


def check_projects_index(workspace: Path) -> list[str]:
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.workspace_paths import project_dir

    errors: list[str] = []
    pf = file_store.load_projects(workspace)
    for rec in pf.projects:
        proj = project_dir(workspace, rec.id)
        if not proj.is_dir():
            errors.append(
                f"projects.json 有 id={rec.id!r}，但目錄不存在："
                f"{workspace.name}/projects/{rec.id}/"
            )
    if pf.active_project_id:
        if not any(p.id == pf.active_project_id for p in pf.projects):
            errors.append(f"active_project_id={pf.active_project_id!r} 不在 projects 清單中")
        active_dir = project_dir(workspace, pf.active_project_id)
        if pf.active_project_id and not active_dir.is_dir():
            errors.append(f"active 專案目錄不存在：projects/{pf.active_project_id}/")
    orphan_dirs = []
    projects_root = workspace / "projects"
    if projects_root.is_dir():
        indexed = {p.id for p in pf.projects}
        for child in projects_root.iterdir():
            if child.is_dir() and child.name not in indexed:
                orphan_dirs.append(child.name)
    if orphan_dirs:
        _warn(f"磁碟上有未列入 projects.json 的專案目錄：{', '.join(orphan_dirs[:8])}")
    return errors


def smoke_create_in_temp() -> list[str]:
    import ai_company.work_flow._register  # noqa: F401
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import get_settings
    from ai_company.schemas.commands import CreateProjectCommand, InitWorkspaceCommand

    errors: list[str] = []
    parent = ROOT / "company_workspace"
    parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="ai-ceo-layout-test-", dir=parent))
    try:
        settings = get_settings().model_copy(update={"company_workspace_root": workspace})
        deps = AppDeps(settings=settings)
        init = dispatch(InitWorkspaceCommand(), deps)
        if not init.success:
            errors.append(f"暫存 init-workspace 失敗：{init.message}")
            return errors
        created = dispatch(CreateProjectCommand(name="Layout-Smoke"), deps)
        if not created.success or not created.project_id:
            errors.append(f"暫存 create_project 失敗：{created.message}")
            return errors
        pid = created.project_id
        expected_company = workspace / "_company"
        expected_project = workspace / "projects" / pid
        if not expected_company.is_dir():
            errors.append("smoke：暫存工作區缺少 _company/")
        if not expected_project.is_dir():
            errors.append(f"smoke：暫存工作區缺少 projects/{pid}/")
        if expected_project.is_dir() and not (expected_project / "shared").is_dir():
            errors.append("smoke：專案殼缺少 shared/")
        wrong = ROOT / "projects" / pid
        if wrong.is_dir():
            errors.append(f"smoke：誤建在 repo 根 projects/{pid}/")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="驗證 company_workspace 目錄布局")
    parser.add_argument(
        "--smoke-create",
        action="store_true",
        help="在 company_workspace 下暫存目錄測建專案殼（結束後刪除）",
    )
    args = parser.parse_args()

    from ai_company.config import get_settings
    from ai_company.schemas.workspace_paths import (
        framework_repo_root,
        project_dir,
        resolve_company_workspace_root,
    )

    print("公司沙盒路徑檢查")
    print("─" * 40)

    repo_root = framework_repo_root()
    settings = get_settings()
    workspace = settings.workspace_root
    configured = settings.company_workspace_root

    _ok(f"framework repo 根：{repo_root}")
    _ok(f"COMPANY_WORKSPACE_ROOT（.env）：{configured!r}" if configured else "COMPANY_WORKSPACE_ROOT：未設（預設 company_workspace）")
    _ok(f"解析後 workspace_root：{workspace}")

    expected_default = resolve_company_workspace_root(Path("company_workspace"))
    if configured is None or str(configured).strip() in ("", "company_workspace"):
        if workspace != expected_default:
            return _fail(f"預期工作區為 {expected_default}，實際為 {workspace}")

    if not workspace.is_relative_to(repo_root) and configured is None:
        _warn("工作區不在 repo 根之下（若為絕對路徑則可能正常）")

    ec = 0
    for err in check_no_legacy_repo_root_dirs(repo_root):
        _fail(err)
        ec = 1
    if ec == 0:
        _ok("repo 根未誤放專案沙盒（或僅剩可刪的 MIGRATED 提示）")

    layout_errors = check_workspace_layout(workspace)
    if layout_errors:
        for err in layout_errors:
            _fail(err)
        ec = 1
    else:
        _ok(f"{workspace.name}/_company/ 與 {workspace.name}/projects/ 存在")

    index_errors = check_projects_index(workspace)
    if index_errors:
        for err in index_errors:
            _fail(err)
        ec = 1
    else:
        _ok("projects.json 與 projects/<id>/ 一致")

    if args.smoke_create:
        print("\n暫存建專案殼（smoke）…")
        smoke_errors = smoke_create_in_temp()
        if smoke_errors:
            for err in smoke_errors:
                _fail(err)
            ec = 1
        else:
            _ok("建殼路徑正確（_company + projects/<id>/ 均在 workspace 下）")

    print()
    if ec == 0:
        print("全部檢查通過。")
    else:
        print("有項目未通過，請修正路徑或執行：python -m ai_company.main init-workspace", file=sys.stderr)
    return ec


if __name__ == "__main__":
    raise SystemExit(main())
