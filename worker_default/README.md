# worker_default — 預設 Worker 模板（框架 repo）

**規格**：[`docs/design/execution-layer-v2.md`](../docs/design/execution-layer-v2.md) §4.0、§4.6  
**路線圖**：[`docs/ROADMAP.md`](../docs/ROADMAP.md) §十六  

本目錄在 **框架 repo** 內，不是 `company_workspace` 沙盒產物。用途：

1. 存放 **canonical 預設後端 Worker**（`backend/`）的 skill 與設定。
2. **E1 測試** 先在此定稿模板，再以 `pytest` 複製到臨時專案沙盒驗證；通過後才接到 `run-step`。
3. PM **`/addworker backend`** 或 CLI **`add-worker backend`** 可從此處 **種子複製** 到 `projects/<id>/workers/backend/`（亦可用 `/setupworkers` 建局，但不會自動複製種子）。

**Skill 執行環境**（三件套、不用 MCP、per-worker `skills/`）：[`SKILL_EXECUTION_ENV.md`](SKILL_EXECUTION_ENV.md)  
**程式 runner**：`src/ai_company/modules/worker_runner/`

## 目錄

```text
worker_default/
├── README.md
├── SKILL_EXECUTION_ENV.md
├── fixtures/           # 測試用任務／需求片段
├── backend/
│   ├── SKILL.md
│   ├── role_skills.yaml
│   └── skills/
└── scheduler/          # 任務分配者（kind: task_scheduler）
    ├── SKILL.md
    ├── role_skills.yaml
    └── skills/
```

## 與專案沙盒的對應

| worker_default | 複製到專案後 |
|----------------|--------------|
| `backend/SKILL.md` | `projects/<id>/workers/backend/SKILL.md` |
| `backend/role_skills.yaml` | `projects/<id>/workers/backend/role_skills.yaml` |
| `backend/skills/` | `projects/<id>/workers/backend/skills/` |
| `scheduler/SKILL.md` | `projects/<id>/workers/scheduler/SKILL.md` |
| `scheduler/skills/` | `projects/<id>/workers/scheduler/skills/` |

另需在專案內具備：`workers.yaml` 一列 `{ id: backend, kind: backend }`、`shared/requirements.md`、任務契約（見 execution-layer-v2 §4.2）。測試用 fixture 會一併建立。

## 測試策略（E1）

- **不**在 TG／Training 專案上手動試跑為第一關。
- **先**跑 `tests/` 內 E1 用例：從 `worker_default/backend/` 種子到 `tempfile` 專案目錄 → 呼叫 backend runner（待實作）→ 斷言測試與 `last_run.json`。
- Training（`d668c955`）可作 **第二關** 手動驗收。

## 修訂

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 初版目錄與 E1 測試順序 |
| 2026-06-25 | 目錄更名 `workerDefault` → `worker_default`（與 `company_workspace` 一致） |
| 2026-06-25 | 新增 `scheduler/` 任務分配者種子（E3 起點） |
