# workerDefault — 預設 Worker 模板（框架 repo）

**規格**：[`docs/design/execution-layer-v2.md`](../docs/design/execution-layer-v2.md) §4.0、§4.6  
**路線圖**：[`docs/ROADMAP.md`](../docs/ROADMAP.md) §十六  

本目錄在 **框架 repo** 內，不是 `company_workspace` 沙盒產物。用途：

1. 存放 **canonical 預設後端 Worker**（`backend/`）的 skill 與設定。
2. **E1 測試** 先在此定稿模板，再以 `pytest` 複製到臨時專案沙盒驗證；通過後才接到 `run-step`。
3. 日後 PM 建局（`/addworker` 等）可從此處 **種子複製** 到 `projects/<id>/workers/<id>/`（E4）。

## 目錄

```text
workerDefault/
├── README.md           # 本檔
└── backend/            # kind: backend 的預設實例（id 建議同目錄名 backend）
    ├── SKILL.md        # 自訂 kind 能力／流程／工具邊界（skill 格式）
    └── role_skills.yaml
```

## 與專案沙盒的對應

| workerDefault | 複製到專案後 |
|---------------|--------------|
| `backend/SKILL.md` | `projects/<id>/workers/backend/SKILL.md` |
| `backend/role_skills.yaml` | `projects/<id>/workers/backend/role_skills.yaml` |

另需在專案內具備：`workers.yaml` 一列 `{ id: backend, kind: backend }`、`shared/requirements.md`、任務契約（見 execution-layer-v2 §4.2）。測試用 fixture 會一併建立。

## 測試策略（E1）

- **不**在 TG／Training 專案上手動試跑為第一關。
- **先**跑 `tests/` 內 E1 用例：從 `workerDefault/backend/` 種子到 `tempfile` 專案目錄 → 呼叫 backend runner（待實作）→ 斷言測試與 `last_run.json`。
- Training（`d668c955`）可作 **第二關** 手動驗收。

## 修訂

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 初版目錄與 E1 測試順序 |
