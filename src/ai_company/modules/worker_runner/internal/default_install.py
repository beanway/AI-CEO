"""從 worker_default/<template>/ 複製種子到專案 workers/<id>/。"""

from __future__ import annotations

import shutil
from pathlib import Path

from ai_company.schemas.documents import WorkerEntry
from ai_company.schemas.workspace_paths import framework_repo_root

# template 名稱 = worker_default 子目錄名；id/kind 見 TEMPLATE_WORKER_ENTRIES
SUPPORTED_DEFAULT_TEMPLATES = frozenset({"backend", "scheduler"})

TEMPLATE_WORKER_ENTRIES: dict[str, WorkerEntry] = {
    "backend": WorkerEntry(id="backend", kind="backend"),
    "scheduler": WorkerEntry(id="scheduler", kind="task_scheduler"),
}


def worker_default_template_dir(template: str) -> Path:
    if template not in SUPPORTED_DEFAULT_TEMPLATES:
        raise ValueError(f"不支援的 worker_default 模板：{template!r}")
    path = framework_repo_root() / "worker_default" / template
    if not path.is_dir():
        raise FileNotFoundError(f"缺少種子目錄：{path}")
    return path


def default_worker_entry_for_template(template: str) -> WorkerEntry:
    if template not in SUPPORTED_DEFAULT_TEMPLATES:
        raise ValueError(f"不支援的 worker_default 模板：{template!r}")
    return TEMPLATE_WORKER_ENTRIES[template]


def copy_worker_default_into_worker_dir(project_root: Path, template: str) -> Path:
    """複製 SKILL.md、role_skills.yaml、skills/ 到 workers/<template>/。"""
    entry = default_worker_entry_for_template(template)
    dest = project_root / "workers" / entry.id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "skills").mkdir(parents=True, exist_ok=True)

    seed = worker_default_template_dir(template)
    for name in ("SKILL.md", "role_skills.yaml"):
        src = seed / name
        if src.is_file():
            shutil.copy2(src, dest / name)

    skills_src = seed / "skills"
    skills_dest = dest / "skills"
    if skills_src.is_dir():
        if skills_dest.exists():
            shutil.rmtree(skills_dest)
        shutil.copytree(skills_src, skills_dest)

    return dest
