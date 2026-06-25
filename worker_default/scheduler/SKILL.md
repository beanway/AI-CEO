# scheduler（預設任務分配者 Worker）

**kind**：`task_scheduler`（內建枚舉）  
**預設 id**：`scheduler`  
**模板來源**：`worker_default/scheduler/` → 複製至 `projects/<id>/workers/scheduler/`

## 職責

- 依使用者完整任務（`pm/scheduler_intake.yaml`）與專案脈絡，完成 **分析** 與 **規劃**。
- 讀取編制（`workers.yaml`）、需求（`shared/requirements.md`）、既有 `pm/` 狀態。
- 產出結構化 **`pm/task_queue.yaml`**（含 kind／worker_id、順序、驗收條件）。
- 為下一個執行者寫入對應任務契約（例：`pm/backend_current_task.yaml`）。
- 完成後寫入 `workers/scheduler/last_run.json`；可追加 `pm/scheduler_decisions.jsonl`（一行一筆 JSON）。

## Skill（本 Worker 各自管理）

- 劇本目錄：**`workers/scheduler/skills/*.md`**（由種子複製）。
- 執行時透過 `list_skills` / `read_skill` 載入。

## 允許路徑（沙盒內）

- 讀：`shared/`、`pm/`、`workers/`（各執行者目錄，供分析）、`workers.yaml`
- 寫：`pm/`、`workers/scheduler/`
- **禁止**修改框架 `src/`、`_company/`、任意執行者程式目錄內的產物

## 工具

- `read_file` / `write_file`（限上述路徑）
- **預設不**使用 `run_terminal`（規劃階段以讀寫與 `complete_task` 為主）
- Git 由框架 PM／高風險核准流程處理；種子 runner 不代為 `git push`

## 流程

1. 讀劇本 `skills/01_analyze_and_plan.md`。
2. 讀 intake、workers.yaml、requirements。
3. 寫入 `pm/task_queue.yaml` 與第一個待執行任務的 `pm/*_current_task.yaml`。
4. 呼叫 `complete_task`（`status=success`）；規劃任務無 pytest 時 `test_exit_code` 可為 0 且 `test_command` 留空。

## 執行環境說明

見 [`../SKILL_EXECUTION_ENV.md`](../SKILL_EXECUTION_ENV.md)。
