#!/usr/bin/env python3
"""在 company_workspace/_company 建立 Git 倉並於 GitHub 建立遠端（gh）。

會先 ensure 工作區與廣域設定檔，寫入 .gitignore（排除 runtime），初始 commit 後 gh repo create --push。

前置：gh auth login、.env 內 GITHUB_OWNER（可選 GITHUB_COMPANY_REPO_NAME、GITHUB_REPO_VISIBILITY）

  .venv/bin/python scripts/bootstrap_company_github_repo.py
  .venv/bin/python scripts/bootstrap_company_github_repo.py --local-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser(description="bootstrap _company GitHub 倉")
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="僅本機 git init／commit，不呼叫 gh",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="建立遠端但不 --push",
    )
    args = parser.parse_args()

    from ai_company.config import get_settings
    from ai_company.modules.company_git_bootstrap import core as company_git
    from ai_company.work_flow._shared.company_workspace import ensure_company_workspace

    settings = get_settings()
    workspace = settings.workspace_root
    print(f"工作區：{workspace}")
    ensure_company_workspace(workspace)

    msg = company_git.bootstrap_company_github(
        workspace,
        settings,
        create_remote=not args.local_only,
        push=not args.no_push,
    )
    print(msg)
    if "失敗" in msg:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
