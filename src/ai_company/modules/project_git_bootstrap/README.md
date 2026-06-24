# project_git_bootstrap

**建專案殼後**：本機 `git init`、專案 `.gitignore`；可選以 **`gh repo create`** 建立 GitHub 遠端（見 `.env`）。

| 環境變數 | 說明 |
|----------|------|
| `GITHUB_AUTO_CREATE_REPO` | `true` 時建專案後呼叫 `gh` |
| `GITHUB_OWNER` | GitHub 使用者或 org 名稱 |
| `GITHUB_REPO_VISIBILITY` | `private`（預設）或 `public` |

前置：`gh auth login`（或 `GH_TOKEN`）。不必在 GitHub 網頁先手動建倉。
