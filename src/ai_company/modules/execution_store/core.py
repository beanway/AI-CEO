"""執行狀態持久化（Phase B）：_company/execution/ 與單一 Worker 佇列。"""

from __future__ import annotations

import json
import secrets
from pathlib import Path

from ai_company.schemas.documents import (
    ExecutionQueueFile,
    ExecutionQueueItem,
    ExecutionStateFile,
    ExecutionStatus,
    utc_now,
)


def execution_dir(workspace_root: Path) -> Path:
    return workspace_root / "_company" / "execution"


def _queue_path(workspace_root: Path) -> Path:
    return execution_dir(workspace_root) / "queue.json"


def _state_path(workspace_root: Path, execution_id: str) -> Path:
    safe = execution_id.replace("/", "_")
    return execution_dir(workspace_root) / f"{safe}.json"


def load_execution_state(workspace_root: Path, execution_id: str) -> ExecutionStateFile | None:
    path = _state_path(workspace_root, execution_id)
    if not path.is_file():
        return None
    return ExecutionStateFile.model_validate_json(path.read_text(encoding="utf-8"))


def save_execution_state(workspace_root: Path, state: ExecutionStateFile) -> None:
    directory = execution_dir(workspace_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = _state_path(workspace_root, state.execution_id)
    tmp = path.with_suffix(".json.tmp")
    updated = state.model_copy(update={"updated_at": utc_now()})
    tmp.write_text(updated.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)


def list_execution_states(workspace_root: Path) -> list[ExecutionStateFile]:
    directory = execution_dir(workspace_root)
    if not directory.is_dir():
        return []
    states: list[ExecutionStateFile] = []
    for path in sorted(directory.glob("*.json")):
        if path.name == "queue.json":
            continue
        try:
            states.append(ExecutionStateFile.model_validate_json(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return states


def list_running_for_project(workspace_root: Path, project_id: str) -> list[ExecutionStateFile]:
    return [
        s
        for s in list_execution_states(workspace_root)
        if s.project_id == project_id and s.status == ExecutionStatus.RUNNING
    ]


def list_running_globally(workspace_root: Path) -> list[ExecutionStateFile]:
    return [s for s in list_execution_states(workspace_root) if s.status == ExecutionStatus.RUNNING]


def interrupt_execution(workspace_root: Path, execution_id: str) -> ExecutionStateFile | None:
    state = load_execution_state(workspace_root, execution_id)
    if state is None:
        return None
    if state.status != ExecutionStatus.RUNNING:
        return state
    updated = state.model_copy(
        update={"status": ExecutionStatus.INTERRUPTED},
    )
    save_execution_state(workspace_root, updated)
    return updated


def load_queue_state(workspace_root: Path) -> ExecutionQueueFile:
    path = _queue_path(workspace_root)
    if not path.is_file():
        return ExecutionQueueFile()
    return ExecutionQueueFile.model_validate_json(path.read_text(encoding="utf-8"))


def save_queue_state(workspace_root: Path, state: ExecutionQueueFile) -> None:
    directory = execution_dir(workspace_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = _queue_path(workspace_root)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)


def enqueue_dispatch(
    workspace_root: Path,
    *,
    project_id: str,
    worker_id: str,
) -> ExecutionQueueItem:
    queue = load_queue_state(workspace_root)
    item = ExecutionQueueItem(project_id=project_id, worker_id=worker_id)
    queue.pending.append(item)
    save_queue_state(workspace_root, queue)
    return item


def dequeue_next_pending(workspace_root: Path) -> ExecutionQueueItem | None:
    queue = load_queue_state(workspace_root)
    if not queue.pending:
        return None
    item = queue.pending.pop(0)
    save_queue_state(workspace_root, queue)
    return item


def peek_next_pending(workspace_root: Path) -> ExecutionQueueItem | None:
    queue = load_queue_state(workspace_root)
    if not queue.pending:
        return None
    return queue.pending[0]


def new_execution_id() -> str:
    return secrets.token_hex(8)
