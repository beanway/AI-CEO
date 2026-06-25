#!/usr/bin/env python3
"""
驗收 /addworker backend（等同 TG AddWorkerCommand）。

用法（repo 根目錄）：
  .venv/bin/python scripts/simulate_addworker_backend.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from simulate_common import bootstrap_imports, make_deps, register_flows

bootstrap_imports()
register_flows()

from ai_company.adapters.dispatch import dispatch
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand, ShowProjectStatusCommand


def main() -> int:
    print("simulate /addworker backend")
    workspace = Path(tempfile.mkdtemp(prefix="ai-ceo-addworker-"))
    deps = make_deps(workspace)
    file_store.ensure_company_dirs(workspace)

    created = dispatch(CreateProjectCommand(name="AddWorkerDemo"), deps)
    if not created.success:
        print(f"建專案失敗：{created.message}", file=sys.stderr)
        return 1
    print(f"  ✓ 專案 {created.project_id}")

    add = dispatch(AddWorkerCommand(template="backend"), deps)
    if not add.success:
        print(f"addworker 失敗：{add.message}", file=sys.stderr)
        return 1
    print(f"  ✓ {add.message}")

    skill = (
        workspace
        / "projects"
        / created.project_id
        / "workers"
        / "backend"
        / "SKILL.md"
    )
    if not skill.is_file():
        print("缺少 workers/backend/SKILL.md", file=sys.stderr)
        return 1
    print("  ✓ worker_default 種子已複製")

    status = dispatch(ShowProjectStatusCommand(), deps)
    if not status.success or "backend" not in status.message:
        print(f"status 異常：{status.message}", file=sys.stderr)
        return 1
    print("  ✓ status 含 backend")
    print(f"\n工作區：{workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
