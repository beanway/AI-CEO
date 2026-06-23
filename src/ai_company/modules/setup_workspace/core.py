"""建立工作區根目錄、遷移舊扁平結構、確保 _company 骨架。"""

from pathlib import Path

from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_workspace.internal import migrate


def ensure_workspace(workspace_root: Path) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    migrate.migrate_flat_workspace(workspace_root)
    file_store.ensure_company_dirs(workspace_root)
    file_store.ensure_company_index_files(workspace_root)
