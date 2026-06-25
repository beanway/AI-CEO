"""將誤建在 framework repo 根的 _company/、projects/ 併入 COMPANY_WORKSPACE_ROOT。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ai_company.schemas.documents import ProjectsFile
from ai_company.schemas.workspace_paths import COMPANY_DIR_NAME, PROJECTS_DIR_NAME

_MIGRATED_TEXT = """\
此目錄已廢棄。全公司索引與設定請使用：

  company_workspace/_company/

並在 .env 設定 COMPANY_WORKSPACE_ROOT=company_workspace（或絕對路徑）。
可安全刪除本目錄。
"""


def migrate_repo_root_company_layout(repo_root: Path, workspace_root: Path) -> list[str]:
    """回傳已遷移項目的簡短說明（供日誌）。"""
    legacy_company = repo_root / COMPANY_DIR_NAME
    legacy_projects = repo_root / PROJECTS_DIR_NAME
    if not legacy_company.is_dir() and not legacy_projects.is_dir():
        return []

    workspace_root.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []

    if legacy_projects.is_dir():
        dest_projects = workspace_root / PROJECTS_DIR_NAME
        dest_projects.mkdir(parents=True, exist_ok=True)
        for child in legacy_projects.iterdir():
            if not child.is_dir() or child.name.startswith("."):
                continue
            target = dest_projects / child.name
            if target.exists():
                continue
            shutil.move(str(child), str(target))
            moved.append(f"projects/{child.name}")

    if legacy_company.is_dir():
        dest_company = workspace_root / COMPANY_DIR_NAME
        dest_company.mkdir(parents=True, exist_ok=True)
        src_pj = legacy_company / "projects.json"
        dst_pj = dest_company / "projects.json"
        if src_pj.is_file():
            _merge_projects_json(dst_pj, src_pj)
            moved.append("_company/projects.json")
            src_pj.unlink()

        for item in legacy_company.iterdir():
            if item.name in ("MIGRATED.txt", "projects.json", ".git"):
                continue
            dest = dest_company / item.name
            if item.is_dir():
                if not dest.exists():
                    shutil.move(str(item), str(dest))
                    moved.append(f"_company/{item.name}/")
                else:
                    _merge_dir_into(item, dest)
                    shutil.rmtree(item, ignore_errors=True)
                    moved.append(f"_company/{item.name}/ (merged)")
            elif item.is_file():
                if not dest.exists():
                    shutil.copy2(item, dest)
                    moved.append(f"_company/{item.name}")
                item.unlink(missing_ok=True)

    _retire_legacy_dir(legacy_projects)
    _retire_legacy_dir(legacy_company)
    return moved


def _merge_projects_json(dest_path: Path, src_path: Path) -> None:
    dest = (
        ProjectsFile.model_validate_json(dest_path.read_text(encoding="utf-8"))
        if dest_path.is_file()
        else ProjectsFile()
    )
    src = ProjectsFile.model_validate_json(src_path.read_text(encoding="utf-8"))
    by_id = {p.id: p for p in dest.projects}
    for rec in src.projects:
        by_id[rec.id] = rec
    dest.projects = list(by_id.values())
    if src.active_project_id:
        dest.active_project_id = src.active_project_id
    elif dest.active_project_id is None and dest.projects:
        dest.active_project_id = dest.projects[0].id
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(
        json.dumps(dest.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _merge_dir_into(src_dir: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for child in src_dir.rglob("*"):
        if child.is_dir():
            continue
        rel = child.relative_to(src_dir)
        target = dest_dir / rel
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(child, target)


def _retire_legacy_dir(path: Path) -> None:
    if not path.is_dir():
        return
    remaining = [p for p in path.iterdir() if p.name != "MIGRATED.txt"]
    if not remaining:
        shutil.rmtree(path, ignore_errors=True)
        return
    (path / "MIGRATED.txt").write_text(_MIGRATED_TEXT, encoding="utf-8")
