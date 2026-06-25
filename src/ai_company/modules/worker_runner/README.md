# worker_runner

**狀態**：E1 **過渡**單體 runner；目標架構見 [`docs/design/worker-sandbox-packages.md`](../../../../docs/design/worker-sandbox-packages.md)，遷移計畫 [`docs/plans/phase-e-worker-packages.md`](../../../../docs/plans/phase-e-worker-packages.md)（E-P2 起由 `worker_host` 取代內嵌邏輯）。

backend／scheduler 的 **Skill 執行環境**（過渡實作）：per-worker `skills/`、harness 工具、`complete_task` → `last_run.json`。

規格：[`worker_default/SKILL_EXECUTION_ENV.md`](../../../../worker_default/SKILL_EXECUTION_ENV.md)
