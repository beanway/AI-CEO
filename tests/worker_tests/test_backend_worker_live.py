"""整合測試：複製 worker_default 種子並以 Gemini 執行 demo 任務。"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_company.modules.settings.core import AppSettings, default_global_config, resolve_model
from ai_company.modules.worker_runner import core as worker_runner
from ai_company.schemas.ai_generation import AiGenerationSettings

SANDBOX_ROOT = Path(__file__).resolve().parent / "_sandbox"
PROJECT_ID = "worker_live_test"
WORKER_ID = "backend"


@pytest.fixture(scope="module")
def live_workspace() -> Path:
    root = SANDBOX_ROOT / "company_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(SANDBOX_ROOT)
    root.mkdir(parents=True)
    worker_runner.seed_backend_worker_project(root, PROJECT_ID, worker_id=WORKER_ID)
    return root


def test_backend_worker_live_gemini(live_workspace: Path):
    settings = AppSettings()
    api_key = settings.resolved_gemini_api_key()
    if not api_key:
        pytest.skip("缺少 GOOGLE_API_KEY / GEMINI_API_KEY（.env）")

    generation = AiGenerationSettings(
        max_output_tokens=8192,
        thinking_budget=0,
        include_thoughts=False,
        temperature=0.2,
    )
    model = resolve_model(default_global_config())

    try:
        result = worker_runner.run_backend_worker_gemini(
            live_workspace,
            PROJECT_ID,
            WORKER_ID,
            api_key=api_key,
            model=model,
            generation=generation,
            max_turns=30,
        )
    except Exception as exc:
        name = type(exc).__name__
        if name == "ClientError" and "429" in str(exc):
            pytest.skip(f"Gemini API 配額限制：{exc}")
        raise

    assert result.success, result.summary
    last = worker_runner.load_last_run(live_workspace, PROJECT_ID, WORKER_ID)
    assert last is not None and last.status == "success"

    calc = (
        live_workspace
        / "projects"
        / PROJECT_ID
        / "workers"
        / WORKER_ID
        / "calc.py"
    )
    assert calc.is_file(), "預期產生 calc.py，請檢查 _sandbox 目錄"
