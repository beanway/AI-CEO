import argparse
import logging
import sys

from ai_company.adapters.dispatch import dispatch
from ai_company.app_deps import AppDeps
from ai_company.config import get_settings
from ai_company.router import run_dual_bots
from ai_company.schemas.commands import Channel, InitWorkspaceCommand


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
        deps = AppDeps(settings=settings)
        result = dispatch(InitWorkspaceCommand(channel=Channel.CLI), deps)
        if not result.success:
            print(result.message, file=sys.stderr)
            sys.exit(1)
        print(result.message)
        return

    try:
        import asyncio

        asyncio.run(run_dual_bots(settings))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
