#!/usr/bin/env python3
"""
Phase B / B+ / C 驗收模擬（roadmap §九–§十一）。

用法（repo 根目錄）：
  .venv/bin/python scripts/simulate_p_b_c_acceptance.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from simulate_common import bootstrap_imports, fail as _fail, make_deps, ok as _ok, register_flows

bootstrap_imports()
register_flows()

from ai_company.adapters.dispatch import dispatch
from ai_company.modules.file_store import core as file_store
from ai_company.modules.notify import core as notify
from ai_company.schemas.commands import (
    CreateProjectCommand,
    ListRegistrySkillsCommand,
    ResolveExecutionFailureCommand,
    RunExecutionStepCommand,
    SetupWorkersCommand,
)


def _ok(label: str) -> None:
    print(f"  ✓ {label}")


def _fail(label: str, detail: str) -> None:
    print(f"  ✗ {label}: {detail}", file=sys.stderr)


def main() -> int:
    print("Phase B/C 驗收模擬")
    workspace = Path(tempfile.mkdtemp(prefix="ai-ceo-b-"))
    deps = make_deps(workspace)
    sent: list[str] = []
    notify.set_notify_sink(lambda _cid, text: sent.append(text))

    file_store.ensure_company_dirs(workspace)
    cfg = file_store.load_global_config(workspace)
    file_store.save_global_config(
        workspace, cfg.model_copy(update={"executor_notify_chat_id": 1})
    )

    created = dispatch(CreateProjectCommand(name="PhaseB"), deps)
    if not created.success:
        _fail("建專案", created.message)
        return 1
    _ok("建專案殼")

    sw = dispatch(SetupWorkersCommand(template="three"), deps)
    if not sw.success:
        _fail("建局 three", sw.message)
        return 1
    _ok("PM 建局（scheduler + planner + qa 模板）")

    fail = dispatch(RunExecutionStepCommand(simulate_failure=True), deps)
    if fail.success or not fail.failure_id:
        _fail("模擬失敗", fail.message)
        return 1
    _ok("Worker 失敗 → pending failure")

    retry = dispatch(
        ResolveExecutionFailureCommand(
            failure_id=fail.failure_id,
            decision="retry",
        ),
        deps,
    )
    if not retry.success:
        _fail("resolve retry", retry.message)
        return 1
    _ok("human-in-the-loop：retry")

    steps = 0
    while steps < 8:
        step = dispatch(RunExecutionStepCommand(), deps)
        steps += 1
        if not step.success:
            _fail("run-step", step.message)
            return 1
        if step.project_done:
            _ok("端到端 pipeline → PROJECT_DONE")
            break
    else:
        _fail("PROJECT_DONE", "超過步數上限")
        return 1

    skills = dispatch(ListRegistrySkillsCommand(), deps)
    if not skills.success:
        _fail("find-skills", skills.message)
        return 1
    _ok(f"find-skills（{len(skills.skill_ids)} 個 registry skill）")

    if not sent:
        _fail("notify", "未收到執行者通知")
        return 1
    _ok("執行者 Bot 通知（sink）")

    log = workspace / "projects" / created.project_id / "pm" / "scheduler_decisions.jsonl"
    if not log.is_file():
        _fail("scheduler_decisions.jsonl", "不存在")
        return 1
    _ok("scheduler_decisions.jsonl 有記錄")

    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
