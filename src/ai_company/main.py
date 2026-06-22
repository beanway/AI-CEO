import argparse
import logging
import sys

from ai_company.config import get_settings
from ai_company.router import run_dual_bots
from ai_company.workspace import ensure_workspace


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="AI 虛擬公司 — Telegram Router")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=("run", "init-workspace"),
        help="run: 啟動雙 Bot；init-workspace: 建立沙盒目錄",
    )
    args = parser.parse_args()
    settings = get_settings()

    if args.command == "init-workspace":
        ensure_workspace(settings.workspace_root)
        print(f"已建立沙盒：{settings.workspace_root}")
        return

    try:
        import asyncio

        ensure_workspace(settings.workspace_root)
        asyncio.run(run_dual_bots(settings))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
