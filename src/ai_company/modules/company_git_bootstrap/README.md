# company_git_bootstrap

在 **`company_workspace/_company/`** 建立獨立 Git 倉並（可選）`gh repo create`。

| 環境變數 | 說明 |
|----------|------|
| `GITHUB_OWNER` | 必填（遠端） |
| `GITHUB_REPO_VISIBILITY` | `private` / `public` |
| `GITHUB_COMPANY_REPO_NAME` | 遠端倉名（預設 `ai-ceo-company`） |

腳本：`scripts/bootstrap_company_github_repo.py`  
`.gitignore` 由 `file_store` 常數定義（排除 sessions、execution、metrics、pending JSON 等）。
