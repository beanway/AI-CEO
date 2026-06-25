# worker_runner

backend Worker 的 **Skill 執行環境**：per-worker `skills/`、`list_skills`／`read_skill`／讀寫檔／`run_terminal`（ToolPolicy）、`complete_task` → `last_run.json`。

**task_scheduler**（任務分配者）：讀 intake、寫 `pm/task_queue.yaml` 與執行者任務契約；`core.run_scheduler_worker_scripted`；種子 `worker_default/scheduler/`、`seed_scheduler_backend_demo_project`。

公開 API：`core.run_backend_worker_scripted`、`core.run_backend_worker_gemini`、`core.run_scheduler_worker_scripted`；種子 `seed_backend_worker_project`／`seed_scheduler_backend_demo_project`；模板 `copy_worker_default_into_worker_dir`（`backend`、`scheduler`）。

規格：[`worker_default/SKILL_EXECUTION_ENV.md`](../../../../worker_default/SKILL_EXECUTION_ENV.md)
