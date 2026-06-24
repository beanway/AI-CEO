#!/usr/bin/env python3
"""P-A1 驗收模擬（roadmap §六）：CEO 列表、建殼、切換、global skill／設定、對話。"""

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
    AddSkillToCompanyCommand,
    CeoChatCommand,
    CreateProjectCommand,
    InitWorkspaceCommand,
    ListProjectsCommand,
    ShowGlobalConfigCommand,
    SwitchProjectCommand,
    UpdateGlobalConfigCommand,
)


def main() -> int:
    print("P-A1（§六）驗收模擬")
    workspace = sim.temp_workspace("ai-ceo-pa1-")
    deps = sim.make_deps(workspace)

    init = dispatch(InitWorkspaceCommand(), deps)
    if not init.success:
        sim.fail("init-workspace", init.message)
        return 1
    sim.ok("init-workspace")

    listed = dispatch(ListProjectsCommand(), deps)
    if not listed.success:
        sim.fail("list_projects", listed.message)
        return 1
    sim.ok("list_projects")

    created = dispatch(CreateProjectCommand(name="PA1-Demo"), deps)
    if not created.success or not created.project_id:
        sim.fail("create_project", created.message)
        return 1
    pid = created.project_id
    sim.ok(f"create_project → {pid}")

    switched = dispatch(SwitchProjectCommand(project_id=pid), deps)
    if not switched.success:
        sim.fail("switch_project", switched.message)
        return 1
    sim.ok("switch_project")

    global_cfg = dispatch(ShowGlobalConfigCommand(), deps)
    if not global_cfg.success:
        sim.fail("show_global_config", global_cfg.message)
        return 1
    sim.ok("show_global_config")

    skill = dispatch(AddSkillToCompanyCommand(skill_id="example-ceo"), deps)
    if not skill.success:
        sim.fail("add_skill_to_company", skill.message)
        return 1
    sim.ok("add_skill_to_company")

    updated = dispatch(UpdateGlobalConfigCommand(dispatch_min_score=0), deps)
    if not updated.success:
        sim.fail("update_global_config", updated.message)
        return 1
    sim.ok("update_global_config")

    chat = dispatch(CeoChatCommand(text="簡短問候"), deps)
    if not chat.success:
        sim.fail("ceo_chat", chat.message)
        return 1
    sim.ok("ceo_chat")

    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
