"""各 worker package 僅依賴自身模組（獨立運作）。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from ai_company.schemas.workspace_paths import framework_repo_root

REPO = framework_repo_root()


def _load_module_from_package(role: str, module: str):
    pkg_root = REPO / "worker_default" / role / "package"
    path = pkg_root / module.replace(".", "/")
    if path.suffix != ".py":
        path = Path(str(path) + ".py")
    spec = importlib.util.spec_from_file_location(f"standalone_{module}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_backend_package_engine_loads():
    mod = _load_module_from_package("backend", "backend_worker.engine")
    assert hasattr(mod, "run_scripted_loop")


def test_scheduler_package_engine_loads():
    mod = _load_module_from_package("scheduler", "scheduler_worker.engine")
    assert hasattr(mod, "run_scripted_loop")


def test_fixtures_loader_loads():
    mod = _load_module_from_package("fixtures", "fixtures_loader.load")
    assert hasattr(mod, "load_demo_scenario")
