#!/usr/bin/env python3
"""P-A2 驗收模擬（roadmap §七）：PM 建局、專案 skill、對話、狀態查詢。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import simulate_common as sim  # noqa: E402

sim.bootstrap_imports()
sim.register_flows()

from ai_company.adapters.dispatch import dispatch  # noqa: E402
from ai_company.schemas.commands import (  # noqa: E402
    AddSkillToProjectCommand,
    Channel,
    CreateProjectCommand,
    InitWorkspaceCommand,
    PmChatCommand,
    SetUserModeCommand,
    SetupWorkersCommand,
    ShowProjectStatusCommand,
    SwitchProjectCommand,
)
from ai_company.schemas.documents import UserMode  # noqa: E402


def main() -> int:
    print("P-A2（§七）驗收模擬")
    workspace = sim.temp_workspace("ai-ceo-pa2-")
    deps = sim.make_deps(workspace)

    if not dispatch(InitWorkspaceCommand(), deps).success:
        sim.fail("init", "失敗")
        return 1
    created = dispatch(CreateProjectCommand(name="PA2"), deps)
    if not created.success or not created.project_id:
        sim.fail("create_project", created.message)
        return 1
    dispatch(SwitchProjectCommand(project_id=created.project_id), deps)
    sim.ok("專案殼就緒")

    mode = dispatch(
        SetUserModeCommand(telegram_user_id=1, mode=UserMode.PM),
        deps,
    )
    if not mode.success:
        sim.fail("set_user_mode pm", mode.message)
        return 1
    sim.ok("PM mode")

    sw = dispatch(SetupWorkersCommand(template="three"), deps)
    if not sw.success:
        sim.fail("setup_workers", sw.message)
        return 1
    sim.ok("setup_workers three")

    skill = dispatch(
        AddSkillToProjectCommand(channel=Channel.CLI, skill_id="example-ceo"),
        deps,
    )
    if not skill.success:
        sim.fail("add_skill_to_project", skill.message)
        return 1
    sim.ok("add_skill_to_project")

    chat = dispatch(PmChatCommand(text="專案狀態？"), deps)
    if not chat.success:
        sim.fail("pm_chat", chat.message)
        return 1
    sim.ok("pm_chat")

    status = dispatch(ShowProjectStatusCommand(), deps)
    if not status.success or "Workers" not in status.message:
        sim.fail("show_project_status", status.message)
        return 1
    sim.ok("show_project_status")

    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
