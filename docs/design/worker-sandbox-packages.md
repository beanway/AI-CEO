# Worker 沙盒三 Package 架構（決策）

**日期**：2026-06-25  
**狀態**：規格已定；程式自 [`plans/phase-e-worker-packages.md`](../plans/phase-e-worker-packages.md) 分步實作  
**上層**：[`harness-design.md`](harness-design.md)、[`execution-layer-v2.md`](execution-layer-v2.md)

---

## 1. 決策摘要

| 主題 | 決策 |
|------|------|
| **邊界** | `worker_default/backend`、`worker_default/scheduler`、`worker_default/fixtures` 為 **三個獨立 package**（種子在框架 repo；執行期複製到專案沙盒） |
| **可演化程式** | 角色邏輯以 **沙盒內 Python package** 為主（PM 可改）；框架 `src/` 僅保留 **薄載入層**（host／ToolPolicy／契約） |
| **PM 維修** | 修 **`projects/<id>/`** 內 worker package、skill、編制；專案 Git 回滾；flow：**resync**（自種子覆寫）、**repair**（健檢清單） |
| **框架邊界** | Worker／PM **不得**把 `src/ai_company` 當產物修改；路徑與 argv 仍受 ToolPolicy |

**過渡**：現有 `modules/worker_runner/`（單體 runner）視為 **E1 原型**；實作計畫逐步改為 `worker_host` + 沙盒 package，完成前兩者並存，測試綠燈後刪除單體邏輯。

---

## 2. 三 Package 職責（互不相依執行邏輯）

```text
worker_default/
├── backend/          # Package A：後端 Worker 種子（skill + package/）
├── scheduler/        # Package B：任務分配者種子
└── fixtures/         # Package C：場景／任務樣本（資料 + 可選載入程式）
```

| Package | 種子路徑 | 沙盒路徑（複製後） | 職責 |
|---------|----------|-------------------|------|
| **backend** | `worker_default/backend/` | `projects/<id>/workers/<id>/` | 任務契約 → 實作與測試 → `last_run.json` |
| **scheduler** | `worker_default/scheduler/` | `projects/<id>/workers/<id>/`（通常 `id=scheduler`） | intake → `pm/task_queue.yaml`、派工契約 |
| **fixtures** | `worker_default/fixtures/` | `projects/<id>/workers/_fixtures/` 或 `pm/fixtures/`（實作時二選一，見計畫 E-P1） | 測試／demo 場景；**不**與 backend／scheduler 共用 Python 模組目錄 |

**依賴規則**

- backend、scheduler、fixtures **不得** import 彼此 package 內部模組。
- 共用契約型別（任務 YAML、`last_run.json` 語意）由框架 `schemas/` 或 **documented JSON/YAML only** 對接。
- 全公司 reusable 慣例仍放 `skills/registry/`，由 `role_skills.yaml` 引用（不變）。

---

## 3. 沙盒目錄結構（目標）

每個 Worker 實例（以 `backend` 為例）：

```text
projects/<project_id>/workers/backend/
├── worker_manifest.yaml    # kind、package 名稱、entrypoint、允許工具摘要
├── SKILL.md
├── role_skills.yaml
├── skills/                 # 劇本（Markdown）
└── package/                # PM 可改之 Python package（種子自 worker_default/backend/package/）
    ├── pyproject.toml      # 或 package 根標記（實作 E-P1 定稿）
    └── backend_worker/
        ├── __init__.py
        └── run.py          # 契約：run(ctx) -> LastRunPayload（細節見 execution-layer-v2 §4.2）
```

**scheduler**、**fixtures** 同型：`package/scheduler_worker/`、`package/fixtures_loader/`（名稱可調，須寫入 manifest）。

**執行**：框架 `worker_host` 在專案根 cwd 下，依 `worker_manifest.yaml` 載入 **沙盒** `package/`（`sys.path` 僅限該 worker 目錄），呼叫 entrypoint；LLM 工具迴圈可包在 package 內或 host 提供（E-P2 定稿）。

---

## 4. 框架 `src/` 與沙盒分工

| 層 | 路徑 | 誰改 |
|----|------|------|
| **Host** | `modules/worker_host/`（新）或過渡期 `worker_runner` | Cursor／框架 PR |
| **沙盒 package** | `projects/.../workers/<id>/package/` | **PM**、Worker、專案 Git |
| **種子** | `worker_default/*/` | 框架發版；PM **resync** 可覆寫（可選保留 `package/` 自訂） |

---

## 5. PM 可改沙盒程式

| 能力 | 說明 |
|------|------|
| **編輯** | 專案 Git 內修改 `workers/<id>/package/`、`skills/`、`SKILL.md` |
| **resync** | 自 `worker_default/<template>/` 還原 skill／manifest；`package/` 可選 `--force`（計畫 E-P5） |
| **repair** | 健檢：`workers.yaml` ↔ 目錄、manifest 缺欄、entrypoint 無法 import（計畫 E-P5） |
| **不允許** | 改框架 `src/`、寫入 repo 外路徑、ToolPolicy 外 argv |

自我迭代：scheduler／backend 失敗 → TG／PM 修沙盒 package → 重跑 execution → 專案 Git 保留修正史。

---

## 6. fixtures Package 語意

- **不是**第四種 Worker kind。
- **是**獨立種子 package：載入 demo 任務到 `pm/`、供 pytest 與 Training 一鍵場景。
- 執行期僅在 PM／測試明確呼叫時運行，不參與一般 execution 佇列。

---

## 7. 與 execution-layer-v2 的關係

- 任務輸入／輸出契約（§4.2）、ToolPolicy、E3 scheduler 產物：**不變**。
- §4.5「程式落點」以本檔為準：**邏輯在沙盒 package**；`run_execution_step` 呼叫 **host + manifest**，非單體 `worker_runner` 內嵌 scheduler／backend 分支（遷移完成後）。

---

## 8. 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 三 package + PM 沙盒程式決策；過渡自 worker_runner 單體 |
| 2026-06-25 | E-P 交付後未完成：[`plans/phase-e-worker-backlog.md`](../plans/phase-e-worker-backlog.md) |
