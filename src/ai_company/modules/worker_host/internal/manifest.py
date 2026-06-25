"""Worker manifest 與 package 載入。"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ai_company.schemas.workspace_paths import framework_repo_root, project_dir


@dataclass(frozen=True)
class WorkerManifest:
    kind: str
    package_dir: str = "package"
    entrypoint_module: str = ""
    scripted_entry: str = "run_scripted"
    execution_step_entry: str = "run_execution_step"
    load_scenario_entry: str = "load_demo_scenario"


def worker_dir(workspace_root: Path, project_id: str, worker_id: str) -> Path:
    return project_dir(workspace_root, project_id) / "workers" / worker_id


def load_manifest(workspace_root: Path, project_id: str, worker_id: str) -> WorkerManifest:
    path = worker_dir(workspace_root, project_id, worker_id) / "worker_manifest.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"缺少 worker_manifest.yaml：{path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return WorkerManifest(
        kind=str(raw.get("kind", "")),
        package_dir=str(raw.get("package_dir", "package")),
        entrypoint_module=str(raw.get("entrypoint_module", "")),
        scripted_entry=str(raw.get("scripted_entry", "run_scripted")),
        execution_step_entry=str(raw.get("execution_step_entry", "run_execution_step")),
        load_scenario_entry=str(raw.get("load_scenario_entry", "load_demo_scenario")),
    )


def import_entrypoint(
    workspace_root: Path,
    project_id: str,
    worker_id: str,
    manifest: WorkerManifest,
) -> Any:
    if not manifest.entrypoint_module:
        raise ValueError("worker_manifest 缺少 entrypoint_module")
    base = worker_dir(workspace_root, project_id, worker_id)
    pkg_root = base / manifest.package_dir
    if not pkg_root.is_dir():
        raise FileNotFoundError(f"缺少 package 目錄：{pkg_root}")
    inserted = str(pkg_root.resolve())
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
        popped = True
    else:
        popped = False
    try:
        return importlib.import_module(manifest.entrypoint_module)
    finally:
        if popped and sys.path and sys.path[0] == inserted:
            sys.path.pop(0)


def fixtures_package_dir(project_root: Path) -> Path:
    return project_root / "workers" / "_fixtures"


def import_fixtures_entrypoint(project_root: Path) -> Any:
    manifest_path = fixtures_package_dir(project_root) / "worker_manifest.yaml"
    if not manifest_path.is_file():
        raise FileNotFoundError("專案尚未安裝 fixtures package（workers/_fixtures/）")
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    manifest = WorkerManifest(
        kind=str(raw.get("kind", "fixtures")),
        package_dir=str(raw.get("package_dir", "package")),
        entrypoint_module=str(raw.get("entrypoint_module", "fixtures_loader.run")),
        load_scenario_entry=str(raw.get("load_scenario_entry", "load_demo_scenario")),
    )
    pkg_root = fixtures_package_dir(project_root) / manifest.package_dir
    inserted = str(pkg_root.resolve())
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
        popped = True
    else:
        popped = False
    try:
        return importlib.import_module(manifest.entrypoint_module)
    finally:
        if popped and sys.path and sys.path[0] == inserted:
            sys.path.pop(0)


def fixtures_seed_root() -> Path:
    return framework_repo_root() / "worker_default"
