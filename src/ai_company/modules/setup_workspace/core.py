"""建立工作區根目錄、遷移舊扁平結構。"""

from pathlib import Path

from ai_company.modules.setup_workspace.internal import migrate, migrate_repo_root
from ai_company.schemas.workspace_paths import framework_repo_root


def ensure_workspace(workspace_root: Path) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    migrate_repo_root_company_layout(framework_repo_root(), workspace_root)
    migrate.migrate_flat_workspace(workspace_root)


def migrate_repo_root_company_layout(repo_root: Path, workspace_root: Path) -> list[str]:
    """將誤建在 framework repo 根的 _company/、projects/ 併入 workspace。"""
    return migrate_repo_root.migrate_repo_root_company_layout(repo_root, workspace_root)
