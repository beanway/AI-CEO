# 執行層 v2 — 真實 Worker 與 AI 排程（產品方向）

**日期**：2026-06-25  
**狀態**：進行中（先實作 **backend Worker**）  
**上層規格**：[`harness-design.md`](harness-design.md)  
**路線圖勾選**：[`../roadmap.md`](../roadmap.md) §十六  

本檔描述 **Phase B 骨架完成後** 的下一階段：把「寫 `.harness_step_done` 標記」換成 **沙盒內 Gemini + 工具**，並逐步把 **任務分配者** 從固定 pipeline 升級為 **AI 任務規劃與排序**。

---

## 1. 終態流程（產品願景）

```text
使用者提問
  → 問題分析（任務分配者／規劃 Agent）
  → 任務列表與順序（結構化）
  → Worker A 執行任務 1
  → 驗證（測試、產物、可選代碼檢查）
  → …下一任務或打回修改…
```

原則：

- **規範一律用 skill**（`skills/registry/`、`project_skills.yaml`、`role_skills.yaml`、`workers/<id>/SKILL.md`）；不另建 rule 檔類型。
- **Harness 不變**：Router 單入口、專案沙盒、ToolPolicy、全公司單一 execution、人機關卡（TG）可並存。
- **PM／任務分配者進階**（AI 建局、逐個 addworker、自動裝 skill）排在 **backend 單角色跑通** 之後。

---

## 2. 現況與落差（程式）

| 項目 | 現況 | 終態 |
|------|------|------|
| Worker 一步 | `complete_worker_harness_step` 寫標記 | `kind` 對應 runner + `ai_core` + 受限工具 |
| 排程 | `task_scheduler.pick_next_worker` 固定 kind 順序 | LLM 產出任務 DAG／順序（scheduler v2） |
| 評分 | 可選 `dispatch_min_score` + 檔案啟發式 | scheduler 決策 + 機械驗證 + 可選 AI 評分 |
| code review | 人選 `retry`／`code_review`（多導向 planner） | scheduler 主導審查與打回（可保留人機關卡） |
| Skill 安裝 | CEO／PM 指令 + YAML | 執行期自動 find/install 為更後階段 |

詳見 [`roadmap.md`](../roadmap.md) §十五「後續產品」。

---

## 3. 實作階段切分

| 階段 | 範圍 | 不做 |
|------|------|------|
| **E1 — backend Worker** | 真實後端執行、測試驗證、`last_run.json` 產物 | AI 排程、PM 新指令 |
| **E2 — 其他 kind** | planner、frontend、qa… 依同契約 | 全自動 skill 生態 |
| **E3 — scheduler v2** | 提問 → 分析 → 任務列表 → 派工 | — |
| **E4 — PM 進階** | `/addworker`、role skill 指令、與核准整合 | — |

**目前焦點：E1。** 實作順序：**先 `workerDefault/` 定稿預設 backend → fixture 測試 → 再接 `run-step`**（見 §4.0）。

---

## 4. E1：backend Worker

### 4.0 `workerDefault/`（E1 起點）

在框架 repo 根目錄新增 **`workerDefault/`**（非沙盒），作為 **預設 Worker 種子**，與 `skills/registry/`（共用 skill 套件）分開：

| 路徑 | 說明 |
|------|------|
| [`workerDefault/README.md`](../../workerDefault/README.md) | 用途、複製規則、測試順序 |
| `workerDefault/backend/SKILL.md` | 預設後端 Worker 能力／路徑／流程（**skill 格式**） |
| `workerDefault/backend/role_skills.yaml` | 預設要啟用的 registry skill id |

**為何先放這裡**

- 不必等 Training 專案或 TG 建局即可迭代模板與 **pytest fixture**。
- 專案內真實路徑仍是 `projects/<id>/workers/backend/`；測試時 **複製** `workerDefault/backend/*` 進 fixture 專案。
- `run-step` 整合排在 workerDefault + 單元／整合測試綠燈之後。

**E1 實作順序（修訂）**

1. ~~任務契約文件化~~（§4.2）  
2. 維護 `workerDefault/backend/`（SKILL + role_skills；必要時補 `fixtures/` 任務樣本）  
3. `skills/registry/` 建立 §4.4 所列 id，並寫入 `role_skills.yaml`  
4. **測試**：`tests/` 從 workerDefault 種子到臨時沙盒，跑 backend runner（尚未接 TG）  
5. ToolPolicy：`backend` argv 白名單  
6. `run_execution_step` 對 `kind=backend` 接 runner  
7. 可選：Training `d668c955` 手動端到端  

### 4.1 沙盒與編制

- `workers.yaml`：`id` + `kind: backend`（例：`id: backend`）。
- 工作區：`projects/<project_id>/workers/<worker_id>/`（建局時建立 `role_skills.yaml`）。
- 讀寫語意（與 harness §5.2 對齊；路徑以本檔為 E1 約定）：
  - **需求**：`shared/requirements.md`
  - **產物**：`workers/<worker_id>/` 內程式與測試；API 說明更新 `shared/api_docs/`
  - **cwd**：subprocess 為專案根（見 `sandbox_runner.worker_sandbox_cwd`）

> 設計表上的頂層 `backend/` 目錄建殼時未必存在；E1 以 `workers/<id>/` + `shared/` 為準，避免與 `setup_project_folders` 不一致。

### 4.2 任務輸入／輸出契約（先檔案／CLI，供 E3 沿用）

**輸入**（暫存例：`pm/backend_current_task.yaml` 或 CLI 參數）：

```yaml
task_id: string
goal: string
acceptance_criteria:
  - string
allowed_paths:
  - string   # 專案內相對路徑前綴
context_refs:
  - string   # 例 shared/requirements.md
```

**輸出**（`workers/<worker_id>/last_run.json`）：

```yaml
task_id: string
status: success | failed
files_changed: [string]
test_result:
  command: string
  exit_code: int
summary: string
notes_for_reviewer: string   # 供 E3 scheduler 使用
```

### 4.3 必須能做到的事（E1 驗收）

1. 讀取任務契約與 `shared/requirements.md`。
2. 在允許路徑內新增／修改程式與測試。
3. 透過 **ToolPolicy 白名單** 執行測試／lint（如 `pytest`、`ruff`），禁止任意 shell。
4. **測試通過** 才標記 execution 完成；失敗可重試 N 次或進 `pending_execution_failure`。
5. 寫入 `last_run.json`；可保留 `.harness_step_done` 僅作過渡或改由 scoring 讀 `last_run.json`。

**E1 預設不做**：backend 自行 `git push`／`pull`（留 scheduler／PM 與核准流程）。

### 4.4 建議 registry skill（`skills/registry/<id>/SKILL.md`）

掛載：CEO global（可選）→ `project_skills.yaml` → 專案內 `workers/backend/role_skills.yaml`（**可由 `workerDefault/backend/role_skills.yaml` 複製**）。

| skill id（建議） | 用途 |
|------------------|------|
| `backend-sandbox-layout` | 沙盒路徑、產物位置、禁止寫 `src/` 框架 |
| `backend-task-contract` | 任務單與 `last_run.json` 語意 |
| `backend-python-service` | 預設 Python 服務結構、env、無 secret 入庫 |
| `backend-api-design` | REST／錯誤格式、`shared/api_docs/` |
| `backend-verify-local` | 改完必跑測試／lint、失敗自我修正一輪 |

第二輪：`backend-read-logs`、`backend-db-migrations`、`backend-security-basics`。

### 4.5 程式落點（實作時）

- 種子：`workerDefault/backend/`；複製邏輯可放在 `work_flow/_shared/` 或測試 helper（E1 先供 pytest 使用）。
- 新增或擴充 `work_flow/*__work_flow`：`run_execution_step` 在 `kind == backend` 時呼叫專用 runner（非僅 `complete_worker_harness_step`）。
- 工具：`modules/sandbox_runner` + `modules/ai_core`；skill 正文經 `skill_registry.resolve_skill_stack` 注入 prompt。
- 測試：**優先** workerDefault 種子 + fixture 專案；其次 Training 小 API 需求。

### 4.6 `workerDefault` 與 registry 分工

| 內容 | 放哪 |
|------|------|
| 此專案 backend **角色** 的流程、路徑、工具邊界 | `workerDefault/backend/SKILL.md` → 複製到 `workers/<id>/SKILL.md`（自訂 kind 語意；內建 backend 亦以此為預設正文） |
| **可重用** 的後端慣例（Python 服務、API 格式、驗證） | `skills/registry/backend-*/SKILL.md`，由 `role_skills.yaml` 引用 |
| 任務單、需求片段（測試用） | 可放 `workerDefault/fixtures/`（選用，E1 測試建立） |

---

## 5. E3 預覽：任務分配者（下一階段，非 E1）

目標行為：

- 輸入：使用者訊息 + `shared/` + `pm/scheduler_decisions.jsonl` + 編制。
- 輸出：任務列表（含順序、負責 `worker_id`／`kind`、驗收條件）。
- 派工：寫入佇列或觸發 `run-step`；完成後 **驗證** → 低分或 CR 失敗 → 打回指定 worker 或 planner。

現有 `task_scheduler.execution_pipeline` 在 E3 前仍為 **fallback**。

---

## 6. 與 Harness 五要素對照

| 要素 | E1 backend |
|------|------------|
| 防護邊界 | 單 execution、沙盒路徑、argv 白名單 |
| 環境裝配 | workers 目錄、skill 疊加、任務契約檔 |
| 工具治理 | ToolPolicy 擴充 `kind=backend` |
| 安全防護 | 無 secret 入庫、TG 核准仍用於 PM 高風險 git |
| 反饋與迭代 | 測試閘 + `last_run.json` + execution 失敗佇列 |

---

## 7. 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 初版：E1 backend 範圍、契約、skill 清單、階段切分 |
| 2026-06-25 | E1 改為先 `workerDefault/` 種子與 fixture 測試，再接 run-step |
