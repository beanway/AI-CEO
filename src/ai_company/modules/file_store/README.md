# file_store

**設定檔讀寫**：`company_workspace/_company/` 內 JSON/YAML（projects、global、user_prefs、sessions）。

## 對外接口（`core.py`）

專案索引：`load_projects`、`set_active_project`、`get_active_project`、`create_project`（含 `sessions/pm_<id>.json` 索引）、`bootstrap_default_project_if_needed`  
全公司設定：`load_global_skills`、`load_global_config`；`ensure_company_index_files` 會建立／補齊 `global_config.yaml` AI 欄位  
Session：`load_ceo_session`、`save_ceo_session`  
基礎：`ensure_company_dirs`、`ensure_company_index_files`

## 呼叫者

僅 `work_flow/*__work_flow/run.py`。
