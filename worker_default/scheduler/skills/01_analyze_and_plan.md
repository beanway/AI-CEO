# 01 — 分析與任務規劃

## 適用

收到「完整任務」intake 時使用本劇本（任務分配者 run）。

## 步驟

1. **讀 intake**：`pm/scheduler_intake.yaml` 的 `user_goal` 與 `context_refs`。
2. **讀編制**：`workers.yaml`，確認有哪些 `kind`／`id` 可派工（backend、frontend、planner 等）。
3. **讀需求**：`shared/requirements.md`（若 context 有列出）。
4. **規劃**：將工作拆成有序子任務，寫入 `pm/task_queue.yaml`（`plan_id`、`summary`、`tasks[]`，每筆含 `task_id`、`kind`、`worker_id`、`goal`、`acceptance_criteria`）。
5. **派第一筆**：依第一個 `tasks[]` 項目，寫入對應契約檔：
   - `kind: backend` → `pm/backend_current_task.yaml`
   - `kind: planner` → `pm/planner_current_task.yaml`（若專案使用）
   - 其他 kind 依專案慣例之 `pm/<kind>_current_task.yaml`
6. **記錄（選用）**：`write_file` 追加一行 JSON 至 `pm/scheduler_decisions.jsonl`（`action: plan_created`）。
7. **結束**：`complete_task`，`status=success`，`summary` 簡述任務數與第一個派工對象。

## 禁止

- 直接修改 `workers/backend/` 等執行者程式目錄。
- 略過 `task_queue.yaml` 僅寫單一任務檔。
