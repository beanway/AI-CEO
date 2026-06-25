"""worker_default 三 package layout 與隔離。"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_company.modules.setup_project_folders import core as project_folders
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.schemas.workspace_paths import framework_repo_root

REPO = framework_repo_root()


def _package_py_files(role: str) -> list[Path]:
    base = REPO / "worker_default" / role / "package"
    return sorted(base.rglob("*.py")) if base.is_dir() else []


def _imports_in_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
    return mods


def test_copy_includes_manifest_and_package(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    dest = worker_runner.copy_worker_default_into_worker_dir(root, "backend")
    assert (dest / "worker_manifest.yaml").is_file()
    assert (dest / "package" / "backend_worker" / "run.py").is_file()


def test_packages_do_not_cross_import():
    role_to_pkg = {
        "backend": "backend_worker",
        "scheduler": "scheduler_worker",
        "fixtures": "fixtures_loader",
    }
    all_pkgs = set(role_to_pkg.values())
    for role, own_pkg in role_to_pkg.items():
        for path in _package_py_files(role):
            mods = _imports_in_file(path)
            leaked = mods & (all_pkgs - {own_pkg})
            assert not leaked, f"{path} 不得 import 其他 worker package：{leaked}"


def test_backend_package_importable_in_sandbox(tmp_path):
    root = tmp_path / "proj"
    project_folders.ensure_project_tree(root)
    worker_runner.copy_worker_default_into_worker_dir(root, "backend")
    import sys

    pkg = root / "workers" / "backend" / "package"
    sys.path.insert(0, str(pkg))
    try:
        import backend_worker.run as br

        assert callable(br.run_scripted)
    finally:
        if sys.path and sys.path[0] == str(pkg):
            sys.path.pop(0)


def test_unknown_template_raises():
    with pytest.raises(ValueError):
        worker_runner.default_worker_entry_for_template("nope")
