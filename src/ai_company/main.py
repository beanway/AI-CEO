import argparse
import logging
import sys

from ai_company.config import get_settings
from ai_company.router import run_dual_bots
from ai_company.services.company_service import CompanyService
from ai_company.store.company_store import CompanyStore
from ai_company.workspace import ensure_workspace


def _company_service(settings) -> CompanyService:
    ensure_workspace(settings.workspace_root)
    store = CompanyStore(settings.workspace_root)
    company = CompanyService(settings.workspace_root, store)
    company.bootstrap_default_project_if_needed()
    return company


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
        company = _company_service(settings)
        company.bootstrap_default_project_if_needed()
        print(f"已建立沙盒：{settings.workspace_root}")
        return

    try:
        import asyncio

        company = _company_service(settings)
        asyncio.run(run_dual_bots(settings, company))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
