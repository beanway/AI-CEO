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

## 路由表

### Telegram（管理者 Bot）

| 指令 | Command |
|------|---------|
| `/projects` | `ListProjectsCommand` |
| `/switch <id>` | `SwitchProjectCommand` |
| `/newproject <名稱>` | `CreateProjectCommand` |
| `/global` | `ShowGlobalConfigCommand` |
| `/addskill <id>` | `AddSkillToCompanyCommand` |
| `/removeskill <id>` | `RemoveSkillFromCompanyCommand` |
| `/updateglobal <欄位> <值>` | `UpdateGlobalConfigCommand`（單欄位） |
| `/mode ceo\|pm` | `SetUserModeCommand` |
| `/status` | `ShowProjectStatusCommand` |
| `/setupworkers five\|three` | `SetupWorkersCommand` |
| `/addworker backend` | `AddWorkerCommand`（`worker_default/backend/` 種子） |
| `/resyncworker <template> [keeppackage]` | `PmResyncWorkerCommand` |
| `/loadfixture <scenario>` | `LoadFixtureScenarioCommand` |
| `/addprojectskill <id>` | `AddSkillToProjectCommand` |
| `/repair [interrupt]` | `PmRepairCommand` |
| `/git …` | `ProjectGitCommand`（可進核准閘道） |
| 核准 callback | `ResolveApprovalCommand` |
| 文字（非指令） | `RouteManagerChatCommand` |

### CLI（`python -m ai_company.adapters.cli`）

| 子命令 | Command |
|--------|---------|
| `init-workspace` | `InitWorkspaceCommand` |
| `projects` | `ListProjectsCommand` |
| `new-project` | `CreateProjectCommand` |
| `switch` | `SwitchProjectCommand` |
| `global` | `ShowGlobalConfigCommand` |
| `add-skill` / `remove-skill` | `AddSkillToCompany` / `RemoveSkillFromCompany` |
| `update-global` | `UpdateGlobalConfigCommand` |
| `ceo-chat` / `pm-chat` | `CeoChat` / `PmChat` |
| `mode` | `SetUserModeCommand` |
| `setup-workers` | `SetupWorkersCommand` |
| `add-worker <template>` | `AddWorkerCommand`（例：`backend`） |
| `resync-worker <template>` | `PmResyncWorkerCommand`（可加 `--keep-package`） |
| `load-fixture-scenario <name>` | `LoadFixtureScenarioCommand` |
| `project-status` | `ShowProjectStatusCommand` |
| `add-project-skill` | `AddSkillToProjectCommand` |
| `project-git` | `ProjectGitCommand` |
| `pm-repair` | `PmRepairCommand` |
| `run-step` | `RunExecutionStepCommand` |
| `resolve-failure` | `ResolveExecutionFailureCommand` |
| `find-skills` / `create-skill` | `ListRegistrySkills` / `CreateRegistrySkill` |
| `coo-report` | `ShowCooReportCommand` |

### Web

| 方法／路徑 | 說明 |
|------------|------|
| `GET /health` | 存活檢查 |
| `POST /api/v1/dispatch` | JSON body = 任一已註冊 `command_type`（預設 `channel=web`） |

完整 flow 列表：[`work_flow/README.md`](../work_flow/README.md) · 模擬驗收：[`docs/ROADMAP.md`](../../docs/ROADMAP.md) §十三
