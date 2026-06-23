from pathlib import Path

PROJECTS_DIR = "projects"

REQUIREMENTS_TEMPLATE = "# 專案需求\n\n（由 CEO / PM 填寫）\n"


def project_dir(workspace_root: Path, project_id: str) -> Path:
    return workspace_root / PROJECTS_DIR / project_id


def ensure_project_tree(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "shared").mkdir(exist_ok=True)
    (project_root / "pm").mkdir(exist_ok=True)
    req = project_root / "shared" / "requirements.md"
    if not req.exists():
        req.write_text(REQUIREMENTS_TEMPLATE, encoding="utf-8")
    for sub in ("api_docs", "builds"):
        (project_root / "shared" / sub).mkdir(parents=True, exist_ok=True)
