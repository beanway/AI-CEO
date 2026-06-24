"""編排 setup_workspace + file_store 索引（避免 setup_workspace 互引 file_store core）。"""

from __future__ import annotations

from pathlib import Path

from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_workspace import core as setup_workspace


def ensure_company_workspace(workspace_root: Path) -> None:
    setup_workspace.ensure_workspace(workspace_root)
    file_store.ensure_company_dirs(workspace_root)
    file_store.ensure_company_index_files(workspace_root)
