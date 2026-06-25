"""沙盒 worker package 健檢。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_company.modules.worker_host.internal.manifest import import_entrypoint, load_manifest, worker_dir


@dataclass(frozen=True)
class WorkerHealthIssue:
    worker_id: str
    code: str
    detail: str


def check_worker_health(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
) -> list[WorkerHealthIssue]:
    issues: list[WorkerHealthIssue] = []
    base = worker_dir(workspace_root, project_id, worker_id)
    if not base.is_dir():
        issues.append(WorkerHealthIssue(worker_id, "missing_dir", f"缺少 {base}"))
        return issues
    for name in ("SKILL.md", "worker_manifest.yaml"):
        if not (base / name).is_file():
            issues.append(WorkerHealthIssue(worker_id, "missing_file", f"缺少 {name}"))
    if not (base / "package").is_dir():
        issues.append(WorkerHealthIssue(worker_id, "missing_package", "缺少 package/"))
        return issues
    try:
        manifest = load_manifest(workspace_root, project_id, worker_id)
        import_entrypoint(workspace_root, project_id, worker_id, manifest)
    except Exception as exc:
        issues.append(WorkerHealthIssue(worker_id, "import_failed", str(exc)))
    return issues
