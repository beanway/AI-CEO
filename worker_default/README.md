# worker_default — 預設 Worker 種子（三獨立 Package）

**規格**：[`docs/design/worker-sandbox-packages.md`](../docs/design/worker-sandbox-packages.md)  
**執行層**：[`docs/design/execution-layer-v2.md`](../docs/design/execution-layer-v2.md)  
**分步實作**：[`docs/plans/phase-e-worker-packages.md`](../docs/plans/phase-e-worker-packages.md)  
**路線圖**：[`docs/roadmap.md`](../docs/roadmap.md) §十六、§十七  

本目錄在 **框架 repo** 內，不是 `company_workspace` 沙盒產物。

## 三 Package（互不相依執行邏輯）

| 目錄 | 職責 |
|------|------|
| **`backend/`** | 後端 Worker 種子：`SKILL.md`、`skills/`、**`package/`**（可演化程式） |
| **`scheduler/`** | 任務分配者種子（`kind: task_scheduler`） |
| **`fixtures/`** | 場景／demo 任務（獨立 package；非 Worker kind） |

複製到專案後，路徑為 `projects/<id>/workers/<worker_id>/`（fixtures 載入路徑見 worker-sandbox-packages §6）。**PM 可修改沙盒內 `package/` 與 skill**，專案 Git 保留迭代。

## 框架程式

- **目標**：`src/ai_company/modules/worker_host/` 載入沙盒 manifest + entrypoint（見 E-P2）。
- **過渡**：`src/ai_company/modules/worker_runner/` 為 E1 單體原型，遷移後刪除內嵌角色邏輯。

**Skill 執行環境**（host 三件套）：[`SKILL_EXECUTION_ENV.md`](SKILL_EXECUTION_ENV.md)

## 目錄（目標 layout，E-P1 補齊 `package/`）

```text
worker_default/
├── README.md
├── SKILL_EXECUTION_ENV.md
├── fixtures/
│   ├── package/              # E-P1+
│   ├── worker_manifest.yaml
│   └── *.yaml / *.md         # 場景資料
├── backend/
│   ├── worker_manifest.yaml
│   ├── SKILL.md
│   ├── role_skills.yaml
│   ├── skills/
│   └── package/
└── scheduler/
    ├── worker_manifest.yaml
    ├── SKILL.md
    ├── role_skills.yaml
    ├── skills/
    └── package/
```

PM **`/addworker backend|scheduler`** 或 CLI **`add-worker`**：自對應子目錄複製種子（E-P5 起支援 **resync** 覆寫）。

## 測試策略

每步驗收見 [`phase-e-worker-packages.md`](../docs/plans/phase-e-worker-packages.md)。**不**以 TG 手動試跑為第一關。

## 修訂

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 初版目錄與 E1 測試順序 |
| 2026-06-25 | 目錄更名 `workerDefault` → `worker_default` |
| 2026-06-25 | 新增 `scheduler/` 種子 |
| 2026-06-25 | 決策：三 package + 沙盒 `package/`；對齊 worker-sandbox-packages |
