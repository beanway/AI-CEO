"""建立工作區根目錄、遷移舊扁平結構。"""

from pathlib import Path

from ai_company.modules.setup_workspace.internal import migrate


def ensure_workspace(workspace_root: Path) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    migrate.migrate_flat_workspace(workspace_root)
