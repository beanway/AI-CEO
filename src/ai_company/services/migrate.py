import shutil
from pathlib import Path

from ai_company.services.project_paths import ensure_project_tree, project_dir

LEGACY_DIRS = (
    "shared",
    "backend_workspace",
    "frontend_workspace",
    "qa_workspace",
    "pm_workspace",
)
DEFAULT_ID = "default"


def migrate_flat_workspace(workspace_root: Path) -> str | None:
    """扁平 company_workspace/* → projects/default/（僅在偵測到舊 shared/ 且尚無 projects/ 時）。"""
    if not (workspace_root / "shared").is_dir():
        return None
    projects_root = workspace_root / "projects"
    if projects_root.exists() and any(projects_root.iterdir()):
        return None
    dest = project_dir(workspace_root, DEFAULT_ID)
    ensure_project_tree(dest)
    for name in LEGACY_DIRS:
        src = workspace_root / name
        if not src.is_dir():
            continue
        target = dest / name
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(src), str(target))
    return DEFAULT_ID
