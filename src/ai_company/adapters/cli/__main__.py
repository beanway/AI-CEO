import argparse
import logging
import sys

from ai_company.adapters.cli import inbound as cli_inbound


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CEO 全公司指令（本機 CLI）")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-workspace", help="建立 _company 索引與預設 YAML")
    sub.add_parser("projects", help="列出專案與 active（等同 /projects）")
    p_new = sub.add_parser("new-project", help="建立專案殼（等同 /newproject）")
    p_new.add_argument("name", help="專案顯示名稱")
    p_switch = sub.add_parser("switch", help="設定 active 專案（等同 /switch）")
    p_switch.add_argument("project_id", help="專案 id")
    sub.add_parser("global", help="顯示 global_skills / global_config")

    args = parser.parse_args(argv)

    if args.command == "init-workspace":
        return cli_inbound.run_init_workspace()
    if args.command == "projects":
        return cli_inbound.run_projects()
    if args.command == "new-project":
        return cli_inbound.run_create_project(args.name)
    if args.command == "switch":
        return cli_inbound.run_switch(args.project_id)
    if args.command == "global":
        return cli_inbound.run_global()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
