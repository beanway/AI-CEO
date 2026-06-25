# backend（預設後端 Worker）

**kind**：`backend`（內建枚舉）  
**模板來源**：`worker_default/backend/` → 複製至 `projects/<id>/workers/backend/`

## 職責

- 依 `shared/requirements.md` 與任務契約（`pm/backend_current_task.yaml`）實作後端程式與測試。
- 產物寫入 `workers/backend/`（本 worker 目錄）與 `shared/api_docs/`。
- 完成後寫入 `workers/backend/last_run.json`（見 execution-layer-v2 §4.2）。

## Skill（本 Worker 各自管理）

- 劇本目錄：**`workers/backend/skills/*.md`**（由種子 `worker_default/backend/skills/` 複製）。
- 執行時透過 `list_skills` / `read_skill` 載入；**不**依賴全公司 `skills/registry/` 共用（可選保留 registry 供 CEO 安裝，E1 以本目錄為準）。

## 允許路徑（沙盒內）

- 讀：`shared/`（含 `requirements.md`、`api_docs/`）、`workers/backend/`、`pm/`（任務契約）
- 寫：`workers/backend/`、`shared/api_docs/`
- **禁止**修改框架 `src/`、`_company/`、其他專案路徑

## 工具（須經 ToolPolicy 白名單）

- `read_file` / `write_file`（限上述路徑）
- `run_terminal`：`pytest`、`python3 -m pytest`、`ruff`（argv 白名單）
- **預設不**執行 `git commit`／`push`／`pull`、不允許 `pip install`

## 流程

1. 讀 `SKILL.md` 與 `skills/` 劇本（工具 `read_skill`）。
2. 讀任務契約與需求。
3. 實作並更新 api 文件（若任務要求）。
4. 執行測試；依 stdout/stderr 修正（輪次上限由 runner 控制）。
5. 呼叫 `complete_task` 寫入 `last_run.json`；僅在測試 exit code 為 0 時可標記 success。

## 執行環境說明

見 [`../SKILL_EXECUTION_ENV.md`](../SKILL_EXECUTION_ENV.md)。
