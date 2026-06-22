"""本機 CEO 全公司指令（對應 Telegram /projects、/switch 等，Phase A1）。"""

from __future__ import annotations

import argparse
import sys

from ai_company.config import get_settings
from ai_company.models.company import ProjectsFile
from ai_company.store.company_store import CompanyStore
from ai_company.workspace import ensure_workspace


def _store() -> CompanyStore:
    settings = get_settings()
    return CompanyStore(settings.workspace_root)


def cmd_init_workspace() -> int:
    settings = get_settings()
    ensure_workspace(settings.workspace_root)
    print(f"已建立沙盒：{settings.workspace_root}")
    return 0


def cmd_projects() -> int:
    store = _store()
    store.ensure_company_dirs()
    data = store.load_projects()
    if not data.projects:
        print("（尚無專案）")
        print(f"active: {data.active_project_id or '—'}")
        return 0
    for p in data.projects:
        mark = " *" if p.id == data.active_project_id else ""
        print(f"  {p.id}{mark}  {p.name}  [{p.status}]")
    print(f"\nactive_project_id: {data.active_project_id or '—'}")
    return 0


def cmd_switch(project_id: str) -> int:
    store = _store()
    store.ensure_company_dirs()
    data = store.load_projects()
    ids = {p.id for p in data.projects}
    if project_id not in ids:
        print(f"錯誤：找不到專案 id={project_id!r}", file=sys.stderr)
        if ids:
            print(f"可用：{', '.join(sorted(ids))}", file=sys.stderr)
        return 1
    data.active_project_id = project_id
    store.save_projects(data)
    print(f"已切換 active 專案 → {project_id}")
    return 0


def cmd_global() -> int:
    store = _store()
    store.ensure_company_dirs()
    skills = store.load_global_skills()
    config = store.load_global_config()
    print("global_skills.yaml")
    if skills.enabled_skill_ids:
        for sid in skills.enabled_skill_ids:
            print(f"  - {sid}")
    else:
        print("  （無啟用 skill）")
    print("\nglobal_config.yaml")
    print(f"  default_model: {config.default_model}")
    print(f"  notification_policy: {config.notification_policy.value}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CEO 全公司指令（本機 CLI）")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-workspace", help="建立 _company 索引與預設 YAML")

    sub.add_parser("projects", help="列出專案與 active（等同 /projects）")

    p_switch = sub.add_parser("switch", help="設定 active 專案（等同 /switch）")
    p_switch.add_argument("project_id", help="專案 id")

    sub.add_parser("global", help="顯示 global_skills / global_config")

    args = parser.parse_args(argv)

    if args.command == "init-workspace":
        return cmd_init_workspace()
    if args.command == "projects":
        return cmd_projects()
    if args.command == "switch":
        return cmd_switch(args.project_id)
    if args.command == "global":
        return cmd_global()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
