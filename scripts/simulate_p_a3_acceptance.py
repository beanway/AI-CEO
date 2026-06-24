#!/usr/bin/env python3
"""
P-A3 驗收模擬（roadmap §八）：越界拒絕、未核准不執行、維修（不依完整狀態機）。

不啟動 Telegram；以 dispatch + 暫存工作區重現 pytest 主路徑，供本機手動簽收。

用法（repo 根目錄）：
  export PYTHONPATH=src
  python scripts/simulate_p_a3_acceptance.py

或：
  .venv/bin/python scripts/simulate_p_a3_acceptance.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from simulate_common import bootstrap_imports, fail as _fail, make_deps, ok as _ok, register_flows

bootstrap_imports()
register_flows()

from ai_company.adapters.dispatch import dispatch  # noqa: E402
from ai_company.modules.execution_store import core as execution_store  # noqa: E402
from ai_company.modules.file_store import core as file_store  # noqa: E402
from ai_company.schemas.commands import (  # noqa: E402
    AddSkillToProjectCommand,
    Channel,
    CreateProjectCommand,
    PmRepairCommand,
    ProjectGitCommand,
    ResolveApprovalCommand,
)
from ai_company.schemas.documents import (  # noqa: E402
    ApprovalStatus,
    ExecutionStateFile,
    ExecutionStatus,
)
from ai_company.schemas.workspace_paths import project_dir  # noqa: E402


def _require_git() -> bool:
    if shutil.which("git") is None:
        _fail("環境", "找不到 git 命令，請安裝 Git 後再跑")
        return False
    return True


def scenario_tool_policy_outside_sandbox(deps: AppDeps, workspace: Path) -> bool:
    print("\n[1/3] 越界拒絕（ToolPolicy）")
    file_store.ensure_company_dirs(workspace)
    created = dispatch(CreateProjectCommand(name="P-A3-Sandbox"), deps)
    if not created.success:
        _fail("建專案", created.message)
        return False
    outside = workspace / "outside_sandbox"
    outside.mkdir()
    result = dispatch(
        ProjectGitCommand(
            git_argv=["-C", str(outside), "status"],
            project_id=created.project_id,
        ),
        deps,
    )
    if result.success or result.error_code != "tool_policy":
        _fail("git -C 沙盒外", f"success={result.success} error_code={result.error_code!r}")
        return False
    _ok(f"git 指向沙盒外 → error_code=tool_policy（{result.message[:60]}…）")

    root = project_dir(workspace, created.project_id)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    ok = dispatch(
        ProjectGitCommand(git_argv=["status"], project_id=created.project_id),
        deps,
    )
    if not ok.success or ok.exit_code != 0:
        _fail("git status 沙盒內", ok.message)
        return False
    _ok("git status 沙盒內 → 成功")
    return True


def scenario_approval_gate(deps: AppDeps, workspace: Path) -> bool:
    print("\n[2/3] 未核准不執行（TG 高風險 Git + 專案 skill）")
    file_store.ensure_company_dirs(workspace)
    created = dispatch(CreateProjectCommand(name="P-A3-Approval"), deps)
    if not created.success:
        _fail("建專案", created.message)
        return False
    pid = created.project_id
    root = project_dir(workspace, pid)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)

    blocked = dispatch(
        ProjectGitCommand(
            channel=Channel.TELEGRAM,
            git_argv=["commit", "-m", "simulated"],
            project_id=pid,
        ),
        deps,
    )
    if blocked.error_code != "approval_required" or not blocked.approval_id:
        _fail("TG commit 未先擋下", f"error_code={blocked.error_code!r}")
        return False
    _ok(f"TG git commit → approval_required（id={blocked.approval_id}）")

    again = dispatch(
        ProjectGitCommand(
            channel=Channel.TELEGRAM,
            git_argv=["commit", "-m", "simulated"],
            project_id=pid,
        ),
        deps,
    )
    if again.error_code != "approval_required":
        _fail("未核准前重送", "應仍為 approval_required")
        return False
    _ok("未核准前重送 commit → 仍 blocked")

    resolved = dispatch(
        ResolveApprovalCommand(approval_id=blocked.approval_id, approved=True),
        deps,
    )
    if not resolved.approved:
        _fail("核准", resolved.message)
        return False
    record = file_store.get_pending_approval(workspace, blocked.approval_id)
    if record is None or record.status != ApprovalStatus.COMPLETED:
        _fail("核准後狀態", f"status={getattr(record, 'status', None)}")
        return False
    _ok("核准後 → pending 標記 COMPLETED（Git 已執行或結束碼已回傳）")

    pending_skill = dispatch(
        AddSkillToProjectCommand(
            channel=Channel.TELEGRAM,
            skill_id="example-ceo",
            project_id=pid,
        ),
        deps,
    )
    if pending_skill.error_code != "approval_required" or not pending_skill.approval_id:
        _fail("TG add project skill", f"error_code={pending_skill.error_code!r}")
        return False
    _ok("TG 專案 skill → approval_required")

    dispatch(
        ResolveApprovalCommand(
            approval_id=pending_skill.approval_id,
            approved=False,
        ),
        deps,
    )
    skills = file_store.load_project_skills(workspace, pid)
    if "example-ceo" in skills.enabled_skill_ids:
        _fail("拒絕 skill", "skill 不應寫入 project_skills.yaml")
        return False
    _ok("拒絕 skill 核准 → 未寫入 project_skills.yaml")
    return True


def scenario_repair_without_full_state_machine(deps: AppDeps, workspace: Path) -> bool:
    print("\n[3/3] 維修／中斷（簡化 execution 檔，非 §九 完整狀態機）")
    file_store.ensure_company_dirs(workspace)
    created = dispatch(CreateProjectCommand(name="P-A3-Repair"), deps)
    if not created.success:
        _fail("建專案", created.message)
        return False
    pid = created.project_id
    execution_store.save_execution_state(
        workspace,
        ExecutionStateFile(
            execution_id="sim-ex-1",
            project_id=pid,
            worker_id="backend",
            status=ExecutionStatus.RUNNING,
        ),
    )

    inspect = dispatch(PmRepairCommand(project_id=pid, interrupt=False), deps)
    if not inspect.success or inspect.running_execution_count != 1:
        _fail("repair 查詢", f"count={getattr(inspect, 'running_execution_count', None)}")
        return False
    _ok("repair 查詢 → running_execution_count=1")

    interrupted = dispatch(PmRepairCommand(project_id=pid, interrupt=True), deps)
    if not interrupted.success or interrupted.interrupted_execution_ids != ["sim-ex-1"]:
        _fail("repair interrupt", str(getattr(interrupted, "interrupted_execution_ids", None)))
        return False
    state = execution_store.load_execution_state(workspace, "sim-ex-1")
    if state is None or state.status != ExecutionStatus.INTERRUPTED:
        _fail("execution 狀態", f"status={getattr(state, 'status', None)}")
        return False
    log_path = project_dir(workspace, pid) / "pm" / "repair_log.jsonl"
    if not log_path.is_file():
        _fail("repair_log", f"缺少 {log_path}")
        return False
    _ok("interrupt → INTERRUPTED + pm/repair_log.jsonl")
    return True


def main() -> int:
    print("P-A3 驗收模擬（roadmap §八）")
    print("工作區：暫存目錄（結束後刪除）")
    if not _require_git():
        return 2

    # 確保 flow 已註冊（與 pytest / main 相同）
    import ai_company.work_flow._register  # noqa: F401

    passed = 0
    failed = 0
    with tempfile.TemporaryDirectory(prefix="p-a3-sim-") as tmp:
        workspace = Path(tmp)
        deps = make_deps(workspace)
        scenarios = (
            scenario_tool_policy_outside_sandbox,
            scenario_approval_gate,
            scenario_repair_without_full_state_machine,
        )
        for fn in scenarios:
            try:
                if fn(deps, workspace):
                    passed += 1
                else:
                    failed += 1
            except subprocess.CalledProcessError as exc:
                _fail(fn.__name__, f"git 子程序失敗：{exc}")
                failed += 1
            except Exception as exc:
                _fail(fn.__name__, str(exc))
                failed += 1

    print("\n── 摘要 ──")
    print(f"  通過場景：{passed}/{passed + failed}")
    if failed:
        print("  結果：FAIL", file=sys.stderr)
        return 1
    print("  結果：PASS（對應 §八：越界拒絕、未核准不執行、維修輕量路徑）")
    print("\n補充：本腳本未測 Telegram Inline callback；實機請用 Bot /git 與核准按鈕。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
