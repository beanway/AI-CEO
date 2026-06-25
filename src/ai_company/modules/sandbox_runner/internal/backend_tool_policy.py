"""backend Worker 檔案路徑與 subprocess argv 白名單。"""

from __future__ import annotations

from pathlib import Path

from ai_company.modules.sandbox_runner.internal.tool_policy import (
    ToolPolicyError,
    project_sandbox_root,
)


def _within_prefix(rel: str, prefixes: tuple[str, ...]) -> bool:
    norm = rel.replace("\\", "/").lstrip("/")
    for p in prefixes:
        base = p.rstrip("/") + "/"
        if norm == p.rstrip("/") or norm.startswith(base):
            return True
    return False


def backend_path_prefixes(worker_id: str) -> tuple[str, ...]:
    wid = worker_id.strip("/")
    return (
        f"workers/{wid}/",
        "shared/",
        "pm/",
    )


def backend_write_prefixes(worker_id: str) -> tuple[str, ...]:
    wid = worker_id.strip("/")
    return (
        f"workers/{wid}/",
        "shared/api_docs/",
    )


def validate_backend_relative_path(
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
    prefixes = backend_write_prefixes(worker_id) if for_write else backend_path_prefixes(worker_id)
    norm = rel_path.replace("\\", "/")
    if not _within_prefix(norm, prefixes):
        raise ToolPolicyError(f"路徑超出 backend 政策：{rel_path!r}")
    resolved = (root / norm).resolve()
    if not str(resolved).startswith(str(root.resolve())):
        raise ToolPolicyError(f"路徑解析超出沙盒：{rel_path!r}")
    return resolved


def validate_backend_argv(argv: list[str]) -> None:
    if not argv:
        raise ToolPolicyError("argv 不可為空")
    exe = Path(argv[0]).name
    if exe == "pytest":
        return
    if exe in ("python3", "python") and len(argv) >= 3 and argv[1] == "-m" and argv[2] == "pytest":
        return
    if exe == "ruff":
        return
    raise ToolPolicyError(f"backend 不允許執行：{argv[0]!r}")
