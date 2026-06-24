"""模擬驗收腳本共用。"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bootstrap_imports() -> None:
    src = ROOT / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def temp_workspace(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def ok(label: str) -> None:
    print(f"  ✓ {label}")


def fail(label: str, detail: str) -> None:
    print(f"  ✗ {label}: {detail}", file=sys.stderr)


def register_flows() -> None:
    import ai_company.work_flow._register  # noqa: F401


def make_deps(workspace: Path):
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.ai_core import core as ai_core

    ai_core.reset_chat_backends_for_tests()
    return AppDeps(
        settings=Settings(
            company_workspace_root=workspace,
            gemini_api_key="",
            google_api_key="",
        )
    )
