# file_store

**設定檔讀寫**：`company_workspace/_company/` 內 JSON/YAML（projects、global、user_prefs、sessions）。

## 對外接口（`core.py`）

專案索引：`load_projects`、`set_active_project`、`get_active_project`、`add_project_record`、`revert_add_project`、`bootstrap_default_project_if_needed`  
專案內 YAML：`load_workers` / `save_workers`、`load_project_skills` / `save_project_skills`（路徑 `projects/<id>/`）  
全公司設定：`load_global_skills`、`load_global_config`；`ensure_company_index_files` 會建立／補齊 `global_config.yaml` AI 欄位  
Session：`load_ceo_session`、`save_ceo_session`、`load_pm_session`、`save_pm_session`、`init_pm_session`、`delete_pm_session`  
基礎：`ensure_company_dirs`、`ensure_company_index_files`、`resolve_project_id`

建專案殼編排在 `work_flow/_shared/create_project_shell.py`。

## 呼叫者

僅 `work_flow/*__work_flow/run.py`（與 `_shared` 編排）。
