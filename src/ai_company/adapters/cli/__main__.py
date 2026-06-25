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
    p_rm = sub.add_parser("remove-skill", help="停用全公司 registry skill")
    p_rm.add_argument("skill_id", help="skills/registry 下的目錄名")
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
    p_aw = sub.add_parser("add-worker", help="PM 從 worker_default 加入 Worker")
    p_aw.add_argument("template", help="例：backend")
    sub.add_parser("project-status", help="專案狀態摘要")
    p_ps = sub.add_parser("add-project-skill", help="啟用專案 project_skills")
    p_ps.add_argument("skill_id")
    p_git = sub.add_parser("project-git", help="在 active 專案沙盒執行 git")
    p_git.add_argument("git_argv", nargs=argparse.REMAINDER, help="git 子命令與參數")
    p_repair = sub.add_parser("pm-repair", help="PM 維修摘要（可加 --interrupt）")
    p_repair.add_argument(
        "--interrupt",
        action="store_true",
        help="手動中斷進行中的 execution 狀態",
    )
    p_step = sub.add_parser("run-step", help="執行層：派工並跑一步 Worker")
    p_step.add_argument(
        "--simulate-failure",
        action="store_true",
        help="測試用：模擬 Worker 失敗",
    )
    p_fail = sub.add_parser("resolve-failure", help="處理 execution 失敗決策")
    p_fail.add_argument("failure_id")
    p_fail.add_argument("decision", choices=("retry", "code_review"))
    p_skills = sub.add_parser("find-skills", help="列出 skills/registry")
    p_skills.add_argument("--query", default=None)
    p_create = sub.add_parser("create-skill", help="建立 registry skill stub")
    p_create.add_argument("skill_id")
    p_create.add_argument("--description", default="")
    sub.add_parser("coo-report", help="COO 用量報表（usage.jsonl）")

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
    if args.command == "remove-skill":
        return cli_inbound.run_remove_skill(args.skill_id)
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
    if args.command == "add-worker":
        return cli_inbound.run_add_worker(args.template)
    if args.command == "project-status":
        return cli_inbound.run_project_status()
    if args.command == "add-project-skill":
        return cli_inbound.run_add_project_skill(args.skill_id)
    if args.command == "project-git":
        argv = args.git_argv
        if argv and argv[0] == "--":
            argv = argv[1:]
        if not argv:
            print("用法：project-git -- <git 子命令...>", file=sys.stderr)
            return 1
        return cli_inbound.run_project_git(argv)
    if args.command == "pm-repair":
        return cli_inbound.run_pm_repair(interrupt=args.interrupt)
    if args.command == "run-step":
        return cli_inbound.run_execution_step(simulate_failure=args.simulate_failure)
    if args.command == "resolve-failure":
        return cli_inbound.run_resolve_execution_failure(args.failure_id, args.decision)
    if args.command == "find-skills":
        return cli_inbound.run_list_registry_skills(query=args.query)
    if args.command == "create-skill":
        return cli_inbound.run_create_registry_skill(
            args.skill_id, description=args.description
        )
    if args.command == "coo-report":
        return cli_inbound.run_coo_report()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
