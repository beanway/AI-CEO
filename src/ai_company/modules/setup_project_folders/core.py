"""專案沙盒路徑與標準資料夾樹。"""

from pathlib import Path

from ai_company.modules.setup_project_folders.internal.layout import (
    ensure_project_tree,
    project_dir,
)
from ai_company.modules.setup_project_folders.internal.worker_kinds import (
    BUILTIN_WORKER_KINDS,
    WORKER_TEMPLATES,
)
from ai_company.schemas.documents import WorkerEntry

__all__ = [
    "project_dir",
    "ensure_project_tree",
    "BUILTIN_WORKER_KINDS",
    "WORKER_TEMPLATES",
    "ensure_worker_directories",
    "is_builtin_kind",
]


def is_builtin_kind(kind: str) -> bool:
    return kind in BUILTIN_WORKER_KINDS


def ensure_worker_directories(project_root: Path, workers: list[WorkerEntry]) -> None:
    workers_root = project_root / "workers"
    workers_root.mkdir(parents=True, exist_ok=True)
    for entry in workers:
        worker_dir = workers_root / entry.id
        worker_dir.mkdir(parents=True, exist_ok=True)
        (worker_dir / "skills").mkdir(parents=True, exist_ok=True)
        role_skills = worker_dir / "role_skills.yaml"
        if not role_skills.exists():
            role_skills.write_text("enabled_skill_ids: []\n", encoding="utf-8")
