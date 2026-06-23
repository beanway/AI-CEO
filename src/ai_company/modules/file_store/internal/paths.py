from pathlib import Path

PROJECTS_DIR_NAME = "projects"


def project_dir(workspace_root: Path, project_id: str) -> Path:
    return workspace_root / PROJECTS_DIR_NAME / project_id
