"""從 worker_default/<template>/ 複製種子到專案 workers/<id>/。"""

from __future__ import annotations

import shutil
from pathlib import Path

from ai_company.schemas.documents import WorkerEntry
from ai_company.schemas.workspace_paths import framework_repo_root

# template 名稱 = worker_default 子目錄名；id/kind 見 TEMPLATE_WORKER_ENTRIES
SUPPORTED_DEFAULT_TEMPLATES = frozenset({"backend", "scheduler"})
FIXTURES_TEMPLATE = "fixtures"

TEMPLATE_WORKER_ENTRIES: dict[str, WorkerEntry] = {
    "backend": WorkerEntry(id="backend", kind="backend"),
    "scheduler": WorkerEntry(id="scheduler", kind="task_scheduler"),
}


def worker_default_template_dir(template: str) -> Path:
    if template not in SUPPORTED_DEFAULT_TEMPLATES and template != FIXTURES_TEMPLATE:
        raise ValueError(f"不支援的 worker_default 模板：{template!r}")
    path = framework_repo_root() / "worker_default" / template
    if not path.is_dir():
        raise FileNotFoundError(f"缺少種子目錄：{path}")
    return path


def default_worker_entry_for_template(template: str) -> WorkerEntry:
    if template not in SUPPORTED_DEFAULT_TEMPLATES:
        raise ValueError(f"不支援的 worker_default 模板：{template!r}")
    return TEMPLATE_WORKER_ENTRIES[template]


def _copy_tree_replace(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def copy_worker_default_into_worker_dir(
    project_root: Path,
    template: str,
    *,
    force_package: bool = True,
) -> Path:
    """複製 SKILL、manifest、skills/、package/ 到 workers/<id>/。"""
    if template == FIXTURES_TEMPLATE:
        return copy_fixtures_package_into_project(project_root, force_package=force_package)

    entry = default_worker_entry_for_template(template)
    dest = project_root / "workers" / entry.id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "skills").mkdir(parents=True, exist_ok=True)

    seed = worker_default_template_dir(template)
    for name in ("SKILL.md", "role_skills.yaml", "worker_manifest.yaml"):
        src = seed / name
        if src.is_file():
            shutil.copy2(src, dest / name)

    skills_src = seed / "skills"
    skills_dest = dest / "skills"
    if skills_src.is_dir():
        _copy_tree_replace(skills_src, skills_dest)

    package_src = seed / "package"
    package_dest = dest / "package"
    if package_src.is_dir() and force_package:
        _copy_tree_replace(package_src, package_dest)
    elif package_src.is_dir() and not package_dest.exists():
        shutil.copytree(package_src, package_dest)

    return dest


def copy_fixtures_package_into_project(
    project_root: Path,
    *,
    force_package: bool = True,
) -> Path:
    """複製 fixtures 種子到 workers/_fixtures/（場景載入用）。"""
    dest = project_root / "workers" / "_fixtures"
    dest.mkdir(parents=True, exist_ok=True)
    seed = worker_default_template_dir(FIXTURES_TEMPLATE)
    for name in ("worker_manifest.yaml",):
        src = seed / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    package_src = seed / "package"
    package_dest = dest / "package"
    if package_src.is_dir() and force_package:
        _copy_tree_replace(package_src, package_dest)
    elif package_src.is_dir() and not package_dest.exists():
        shutil.copytree(package_src, package_dest)
    data_dest = dest / "fixtures"
    for item in seed.iterdir():
        if item.name in ("package", "worker_manifest.yaml", "README.md"):
            continue
        if item.is_file():
            data_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, data_dest / item.name)
    return dest


def worker_default_root() -> Path:
    return framework_repo_root() / "worker_default"
