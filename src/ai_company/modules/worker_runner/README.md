# worker_runner

backend Worker 的 **Skill 執行環境**：per-worker `skills/`、`list_skills`／`read_skill`／讀寫檔／`run_terminal`（ToolPolicy）、`complete_task` → `last_run.json`。

公開 API：`core.run_backend_worker_scripted`、`core.run_backend_worker_gemini`、`core.load_last_run`；種子 `internal.seed.seed_backend_worker_project`。

規格：[`worker_default/SKILL_EXECUTION_ENV.md`](../../../../worker_default/SKILL_EXECUTION_ENV.md)
