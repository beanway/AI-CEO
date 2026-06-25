"""task_scheduler Worker 檔案路徑白名單。"""

from __future__ import annotations

from pathlib import Path

from ai_company.modules.sandbox_runner.internal.backend_tool_policy import _within_prefix
from ai_company.modules.sandbox_runner.internal.tool_policy import (
    ToolPolicyError,
    project_sandbox_root,
)


def scheduler_read_prefixes(worker_id: str) -> tuple[str, ...]:
    wid = worker_id.strip("/")
    return (
        "shared/",
        "pm/",
        "workers/",
        f"workers/{wid}/",
    )


def scheduler_write_prefixes(worker_id: str) -> tuple[str, ...]:
    wid = worker_id.strip("/")
    return (
        "pm/",
        f"workers/{wid}/",
    )


def _is_workers_yaml(rel: str) -> bool:
    norm = rel.replace("\\", "/").lstrip("/")
    return norm == "workers.yaml"


def validate_scheduler_relative_path(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    rel_path: str,
    *,
    for_write: bool,
) -> Path:
    if not rel_path or rel_path.startswith("/") or ".." in Path(rel_path).parts:
        raise ToolPolicyError(f"不允許的路徑：{rel_path!r}")
    root = project_sandbox_root(workspace_root, project_id)
    norm = rel_path.replace("\\", "/")

    if for_write:
        if _is_workers_yaml(norm):
            raise ToolPolicyError("任務分配者不可寫入 workers.yaml")
        prefixes = scheduler_write_prefixes(worker_id)
        if not _within_prefix(norm, prefixes):
            raise ToolPolicyError(f"路徑超出 task_scheduler 寫入政策：{rel_path!r}")
    else:
        if _is_workers_yaml(norm):
            resolved = (root / "workers.yaml").resolve()
            if not str(resolved).startswith(str(root.resolve())):
                raise ToolPolicyError(f"路徑解析超出沙盒：{rel_path!r}")
            return resolved
        prefixes = scheduler_read_prefixes(worker_id)
        if not _within_prefix(norm, prefixes):
            raise ToolPolicyError(f"路徑超出 task_scheduler 讀取政策：{rel_path!r}")

    resolved = (root / norm).resolve()
    if not str(resolved).startswith(str(root.resolve())):
        raise ToolPolicyError(f"路徑解析超出沙盒：{rel_path!r}")
    return resolved
