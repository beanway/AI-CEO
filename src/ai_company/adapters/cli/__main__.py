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
    p_skill = sub.add_parser("add-skill", help="啟用全公司 registry skill")
    p_skill.add_argument("skill_id", help="skills/registry 下的目錄名")
    p_cfg = sub.add_parser("update-global", help="更新 global_config.yaml 欄位")
    p_cfg.add_argument("--model", dest="default_model", help="default_model")
    p_cfg.add_argument(
        "--notification-policy",
        dest="notification_policy",
        choices=("all", "failures_only", "off"),
    )
    p_cfg.add_argument("--max-output-tokens", type=int, dest="max_output_tokens")
    p_cfg.add_argument("--thinking-budget", type=int, dest="thinking_budget")
    p_cfg.add_argument(
        "--include-thoughts",
        action=argparse.BooleanOptionalAction,
        default=None,
        dest="include_thoughts",
    )
    p_cfg.add_argument("--temperature", type=float, default=None)
    p_chat = sub.add_parser("ceo-chat", help="CEO 對話一則（等同 TG 文字訊息）")
    p_chat.add_argument("text", help="使用者訊息")
    p_mode = sub.add_parser("mode", help="切換 CEO/PM 模式（CLI user id=0）")
    p_mode.add_argument("role", choices=("ceo", "pm"))
    p_pm = sub.add_parser("pm-chat", help="PM 對話一則（需 active 專案）")
    p_pm.add_argument("text", help="使用者訊息")
    p_sw = sub.add_parser("setup-workers", help="PM 建局模板 five|three")
    p_sw.add_argument("template", choices=("five", "three"))
    sub.add_parser("project-status", help="專案狀態摘要")
    p_ps = sub.add_parser("add-project-skill", help="啟用專案 project_skills")
    p_ps.add_argument("skill_id")

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
    if args.command == "add-skill":
        return cli_inbound.run_add_skill(args.skill_id)
    if args.command == "update-global":
        return cli_inbound.run_update_global_config(
            default_model=args.default_model,
            notification_policy=args.notification_policy,
            max_output_tokens=args.max_output_tokens,
            thinking_budget=args.thinking_budget,
            include_thoughts=args.include_thoughts,
            temperature=args.temperature,
        )
    if args.command == "ceo-chat":
        return cli_inbound.run_ceo_chat(args.text)
    if args.command == "mode":
        return cli_inbound.run_mode(args.role)
    if args.command == "pm-chat":
        return cli_inbound.run_pm_chat(args.text)
    if args.command == "setup-workers":
        return cli_inbound.run_setup_workers(args.template)
    if args.command == "project-status":
        return cli_inbound.run_project_status()
    if args.command == "add-project-skill":
        return cli_inbound.run_add_project_skill(args.skill_id)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
