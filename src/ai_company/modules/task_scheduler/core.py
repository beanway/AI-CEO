"""專案內 Worker 排程（task_scheduler kind 語意）。"""

from __future__ import annotations

from ai_company.schemas.documents import (
    ProjectHarnessStateFile,
    ProjectLifecycle,
    WorkerEntry,
    WorkersFile,
)

_KIND_PIPELINE = (
    "task_scheduler",
    "planner",
    "backend",
    "frontend",
    "qa",
)


def execution_pipeline(workers: WorkersFile) -> list[str]:
    """依 kind 排序的 worker id 列表（同 kind 保留 yaml 順序）。"""
    buckets: dict[str, list[str]] = {k: [] for k in _KIND_PIPELINE}
    extras: list[str] = []
    for entry in workers.workers:
        if entry.kind in buckets:
            buckets[entry.kind].append(entry.id)
        else:
            extras.append(entry.id)
    ordered: list[str] = []
    for kind in _KIND_PIPELINE:
        ordered.extend(buckets[kind])
    ordered.extend(extras)
    return ordered


def pick_next_worker(
    workers: WorkersFile,
    harness: ProjectHarnessStateFile,
) -> tuple[str | None, ProjectHarnessStateFile]:
    """
    回傳下一個要執行的 worker id；None 表示專案已 PROJECT_DONE 或無編制。
    """
    if harness.lifecycle == ProjectLifecycle.PROJECT_DONE:
        return None, harness
    pipeline = execution_pipeline(workers)
    if not pipeline:
        return None, harness
    last = harness.last_completed_worker_id
    if last is None:
        return pipeline[0], harness
    if last not in pipeline:
        return pipeline[0], harness
    idx = pipeline.index(last)
    if idx + 1 >= len(pipeline):
        return None, harness.model_copy(update={"lifecycle": ProjectLifecycle.PROJECT_DONE})
    return pipeline[idx + 1], harness


def worker_entry_by_id(workers: WorkersFile, worker_id: str) -> WorkerEntry | None:
    for entry in workers.workers:
        if entry.id == worker_id:
            return entry
    return None


def scheduler_worker_id(workers: WorkersFile) -> str | None:
    for entry in workers.workers:
        if entry.kind == "task_scheduler":
            return entry.id
    return None
