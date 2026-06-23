"""架構守門：modules/*/internal 僅能由同模組 core 或 internal 引用。"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = ("src", "tests", "scripts")


def _owning_module(relative: Path) -> str | None:
    parts = relative.parts
    try:
        idx = parts.index("modules")
    except ValueError:
        return None
    if idx + 2 >= len(parts):
        return None
    name = parts[idx + 1]
    tail = parts[idx + 2]
    if tail == "core.py":
        return name
    if tail == "internal":
        return name
    return None


def _target_module_from_import(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) < 4:
        return None
    if parts[0] != "ai_company" or parts[1] != "modules":
        return None
    if parts[3] != "internal" and not any(p == "internal" for p in parts[3:]):
        return None
    return parts[2]


def _internal_imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "modules." in node.module:
            if ".internal" in node.module:
                hits.append((node.lineno, node.module))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if ".modules." in alias.name and ".internal" in alias.name:
                    hits.append((node.lineno, alias.name))
    return hits


def test_module_internal_import_encapsulation() -> None:
    violations: list[str] = []
    for scan in SCAN_ROOTS:
        root = REPO_ROOT / scan
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT)
            owner = _owning_module(rel)
            for lineno, imported in _internal_imports(path):
                target = _target_module_from_import(imported)
                if target is None:
                    continue
                if owner != target:
                    violations.append(f"{rel}:{lineno}: {imported}")
    assert not violations, "非法引用 modules/*/internal：\n" + "\n".join(violations)
