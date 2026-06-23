"""執行狀態持久化（Phase B）：_company/execution/ 與單一 Worker 佇列。"""

from __future__ import annotations

from pathlib import Path

_NOT_IMPLEMENTED = "execution_store 尚未實作（Phase B）"


def execution_dir(workspace_root: Path) -> Path:
    return workspace_root / "_company" / "execution"


def load_queue_state(workspace_root: Path) -> None:
    raise NotImplementedError(_NOT_IMPLEMENTED)


def save_queue_state(workspace_root: Path, state: object) -> None:
    raise NotImplementedError(_NOT_IMPLEMENTED)
