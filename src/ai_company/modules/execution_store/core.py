"""執行狀態持久化（Phase B）：_company/execution/ 與單一 Worker 佇列。"""

from __future__ import annotations

import json
from pathlib import Path

from ai_company.schemas.documents import ExecutionStateFile, ExecutionStatus

_NOT_IMPLEMENTED = "execution_store 佇列 API 尚未實作（Phase B）"


def execution_dir(workspace_root: Path) -> Path:
    return workspace_root / "_company" / "execution"


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
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)


def list_execution_states(workspace_root: Path) -> list[ExecutionStateFile]:
    directory = execution_dir(workspace_root)
    if not directory.is_dir():
        return []
    states: list[ExecutionStateFile] = []
    for path in sorted(directory.glob("*.json")):
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


def load_queue_state(workspace_root: Path) -> None:
    raise NotImplementedError(_NOT_IMPLEMENTED)


def save_queue_state(workspace_root: Path, state: object) -> None:
    raise NotImplementedError(_NOT_IMPLEMENTED)
