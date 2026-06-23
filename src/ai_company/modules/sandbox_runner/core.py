"""沙盒 subprocess 與 ToolPolicy（Phase B）。"""

from __future__ import annotations

from pathlib import Path

_NOT_IMPLEMENTED = "sandbox_runner 尚未實作（Phase B）"


def run_in_sandbox(
    *,
    cwd: Path,
    argv: list[str],
    allowed_roots: list[Path],
) -> int:
    raise NotImplementedError(_NOT_IMPLEMENTED)
