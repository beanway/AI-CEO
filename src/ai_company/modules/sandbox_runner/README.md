# sandbox_runner

**沙盒指令執行**：Worker subprocess 的 `cwd` 為 `projects/<id>/` 根；依 Worker kind 限制可寫路徑（Phase B）。

`run_in_sandbox` 已改為 **`run_git_in_project_sandbox`**（P-A3 ToolPolicy + 專案 cwd）。
