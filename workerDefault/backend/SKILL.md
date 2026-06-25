# backend（預設後端 Worker）

**kind**：`backend`（內建枚舉）  
**模板來源**：`workerDefault/backend/` → 複製至 `projects/<id>/workers/backend/`

## 職責

- 依 `shared/requirements.md` 與任務契約（`pm/backend_current_task.yaml`）實作後端程式與測試。
- 產物寫入 `workers/backend/`（本 worker 目錄）與 `shared/api_docs/`。
- 完成後寫入 `workers/backend/last_run.json`（見 execution-layer-v2 §4.2）。

## 允許路徑（沙盒內）

- 讀：`shared/`（含 `requirements.md`、`api_docs/`）
- 寫：`workers/backend/`、`shared/api_docs/`
- **禁止**修改框架 `src/`、`_company/`、其他專案路徑

## 工具（須經 ToolPolicy 白名單）

- 讀寫檔案（限上述路徑）
- 子程序：`pytest`、`ruff`（版本與參數由執行層白名單約束）
- **預設不**執行 `git commit`／`push`／`pull`（留任務分配者／PM）

## 流程

1. 載入 skill 疊加（global → project → `role_skills.yaml`）。
2. 讀任務契約與需求。
3. 實作並更新 api 文件。
4. 執行測試／lint；失敗則修正一輪後再回報。
5. 輸出 `last_run.json`；僅在測試通過時標記 execution 成功。

## 關聯 registry skill

見 `role_skills.yaml`；完整清單定義於 execution-layer-v2 §4.4（實作時同步建立於 `skills/registry/`）。
