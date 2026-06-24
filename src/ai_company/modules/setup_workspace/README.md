# setup_workspace

**工作區根目錄建立**：遷移舊扁平目錄。`_company` 索引由 `init_workspace` flow 經 `work_flow/_shared/company_workspace` 與 `file_store` 編排。

## 對外接口（`core.py`）

- `ensure_workspace(workspace_root)` — 僅建立根目錄與遷移
