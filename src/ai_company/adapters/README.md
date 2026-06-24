# adapters — 通道層

將 **Telegram / CLI / Web** 的輸入轉成 `schemas.commands`，經 **`dispatch.dispatch`** 執行已註冊的 `work_flow`。

## 檔案

| 檔案 | 說明 |
|------|------|
| `deps.py` | 轉 re-export `app_deps.AppDeps` |
| `dispatch.py` | 統一入口 → `work_flow.dispatch` |
| `cli/` | `python -m ai_company.adapters.cli` |
| `telegram/` | 管理者／執行者 Bot handler |
| [`web/`](web/README.md) | HTTP `POST /api/v1/dispatch` |

## 路由表（摘要）

| 通道 | 觸發 | Command |
|------|------|---------|
| TG | `/projects` | `ListProjectsCommand` |
| TG | `/switch` `/newproject` `/addskill` | `Switch` / `Create` / `AddSkillToCompany` |
| TG | `/mode` `/status` `/repair` `/setupworkers` … | 對應 PM／維修／建局 flow |
| TG | `/git`、核准 callback | `ProjectGit` / `ResolveApproval` |
| TG | 文字（非指令） | `RouteManagerChatCommand` |
| CLI | `projects` `switch` `global` `ceo-chat` `pm-chat` … | 同左語意 |
| CLI | `run-step` `coo-report` `find-skills` … | Phase B／二期 flow |
| Web | `POST /api/v1/dispatch` | 任意已註冊 `command_type` JSON |

完整 flow 列表：[`work_flow/README.md`](../work_flow/README.md) · 模擬驗收：[`docs/ROADMAP.md`](../../docs/ROADMAP.md) §十三
