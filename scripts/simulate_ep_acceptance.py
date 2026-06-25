#!/usr/bin/env python3
"""
E-P 端對端驗收：addworker → load-fixture → run-step → resync（離線 dispatch）。

用法（repo 根目錄）：
  .venv/bin/python scripts/simulate_ep_acceptance.py
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
from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.schemas.commands import (
    AddWorkerCommand,
    CreateProjectCommand,
    LoadFixtureScenarioCommand,
    PmResyncWorkerCommand,
    RunExecutionStepCommand,
)


def main() -> int:
    print("simulate E-P acceptance (三沙盒 package + worker_host)")
    workspace = Path(tempfile.mkdtemp(prefix="ai-ceo-ep-"))
    deps = make_deps(workspace)
    file_store.ensure_company_dirs(workspace)

    created = dispatch(CreateProjectCommand(name="EPAccept"), deps)
    if not created.success:
        print(f"建專案失敗：{created.message}", file=sys.stderr)
        return 1
    pid = created.project_id
    print(f"  ✓ 專案 {pid}")

    add = dispatch(AddWorkerCommand(template="backend"), deps)
    if not add.success:
        print(f"addworker 失敗：{add.message}", file=sys.stderr)
        return 1
    manifest = (
        workspace
        / "projects"
        / pid
        / "workers"
        / "backend"
        / "worker_manifest.yaml"
    )
    if not manifest.is_file():
        print("缺少 worker_manifest.yaml（E-P1）", file=sys.stderr)
        return 1
    print("  ✓ backend 種子含 manifest + package")

    load = dispatch(LoadFixtureScenarioCommand(scenario="backend_demo"), deps)
    if not load.success:
        print(f"load-fixture 失敗：{load.message}", file=sys.stderr)
        return 1
    print(f"  ✓ {load.message}")

    step = dispatch(RunExecutionStepCommand(project_id=pid), deps)
    if not step.success:
        print(f"run-step 失敗：{step.message}", file=sys.stderr)
        return 1
    last = worker_runner.load_last_run(workspace, pid, "backend")
    if last is None or last.status != "success":
        print("last_run.json 未成功（E-P6 / worker_host）", file=sys.stderr)
        return 1
    print(f"  ✓ run-step backend · {last.summary or last.status}")

    root = project_folders.project_dir(workspace, pid)
    pkg = root / "workers" / "backend" / "package" / "backend_worker" / "run.py"
    pkg.write_text("# tampered\n", encoding="utf-8")
    resync = dispatch(
        PmResyncWorkerCommand(template="backend", force_package=True),
        deps,
    )
    if not resync.success or "run_scripted" not in pkg.read_text(encoding="utf-8"):
        print(f"resync 失敗：{resync.message}", file=sys.stderr)
        return 1
    print("  ✓ resync 還原 package")

    print(f"\n工作區：{workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
