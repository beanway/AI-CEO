# adapters — 通道層

將 **Telegram / CLI /（二期）Web** 的輸入轉成 `schemas.commands`，經 **`dispatch.dispatch`** 執行已註冊的 `work_flow`。

## 檔案

| 檔案 | 說明 |
|------|------|
| `deps.py` | 轉 re-export `app_deps.AppDeps` |
| `dispatch.py` | 統一入口 → `work_flow.dispatch` |
| `cli/` | `python -m ai_company.adapters.cli`（`ceo_cli` 轉發） |
| `telegram/` | 管理者／執行者 Bot handler |
| [`web/`](web/README.md) | HTTP `POST /api/v1/dispatch`（第二期） |

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
