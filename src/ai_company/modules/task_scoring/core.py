"""Worker 產物結構化評分（0–100）。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_company.modules.file_store import core as file_store
from ai_company.schemas.workspace_paths import project_dir


@dataclass(frozen=True)
class TaskScore:
    worker_id: str
    value: int
    reasons: tuple[str, ...]


def score_worker_output(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> TaskScore:
    root = project_dir(workspace_root, project_id)
    workers = file_store.load_workers(workspace_root, project_id)
    entry = next((w for w in workers.workers if w.id == worker_id), None)
    kind = entry.kind if entry else "unknown"
    worker_path = root / "workers" / worker_id
    reasons: list[str] = []
    score = 0

    marker = worker_path / ".harness_step_done"
    if marker.is_file():
        score += 40
        reasons.append("step_marker")
    else:
        reasons.append("missing_step_marker")

    req = root / "shared" / "requirements.md"
    if kind in ("planner", "task_scheduler", "qa") and req.is_file():
        score += 20
        reasons.append("requirements_present")

    if kind == "qa":
        qa_pass = root / "shared" / "qa_passed.txt"
        if qa_pass.is_file():
            score += 40
            reasons.append("qa_passed")
        else:
            reasons.append("qa_not_passed")
    elif kind in ("backend", "frontend"):
        if worker_path.is_dir() and any(worker_path.iterdir()):
            score += 30
            reasons.append("worker_dir_nonempty")
    else:
        score += 10
        reasons.append("baseline_kind")

    score = min(100, score)
    return TaskScore(worker_id=worker_id, value=score, reasons=tuple(reasons))


def passes_dispatch_gate(
    workspace_root: Path,
    project_id: str,
    *,
    previous_worker_id: str,
    min_score: int,
) -> tuple[bool, TaskScore]:
    result = score_worker_output(workspace_root, project_id, previous_worker_id)
    return result.value >= min_score, result
