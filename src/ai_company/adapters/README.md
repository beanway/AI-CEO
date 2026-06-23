# adapters — 通道層

將 **Telegram / CLI /（二期）Web** 的輸入轉成 `schemas.commands`，經 **`dispatch.dispatch`** 執行已註冊的 `work_flow`。

## Phase A0：目錄與實作對照

| 規格位置 | 目前實作 | 說明 |
|----------|----------|------|
| `adapters/telegram/` | **`src/ai_company/telegram/`** | 語意上屬通道層；A1 可遷移至 `adapters/telegram/` |
| `adapters/cli/inbound.py` | 已存在 | `ceo_cli.py` 仍為 CLI 入口腳本，委派此模組 |

## 檔案

| 檔案 | 說明 |
|------|------|
| `deps.py` | 轉 re-export `app_deps.AppDeps` |
| `dispatch.py` | 統一入口 → `work_flow.dispatch` |
| `cli/inbound.py` | argv 子命令 → Command |
| `telegram/` | （目標）TG 適配；現用套件根下 `telegram/` |

## 路由表（Phase A）

| 通道 | 觸發 | Command |
|------|------|---------|
| TG | `/projects` | `ListProjectsCommand` |
| TG | `/switch <id>` | `SwitchProjectCommand` |
| CLI | `projects` | `ListProjectsCommand` |
| CLI | `switch` | `SwitchProjectCommand` |
| CLI / main | `init-workspace` | `InitWorkspaceCommand` |
| CLI | `global` | `ShowGlobalConfigCommand` |

完整 flow 列表：[`work_flow/README.md`](../work_flow/README.md)
