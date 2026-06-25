# 實作路線圖

**角色**：本檔是 **「做什麼、先做什麼、怎麼驗收」** 的總表；細節規格見下表。

| 主題 | 文件 |
|------|------|
| 產品／CEO·PM·Worker | [`design/harness-design.md`](design/harness-design.md) |
| 程式分層、modules、work_flow | [`design/src-layout.md`](design/src-layout.md) |
| A1 模組遷移拆解 | [`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md) |
| 共識摘要 | [`discussion-outcomes.md`](discussion-outcomes.md) |

**原則**：新能力一律 **Command → `adapters.dispatch` → `*__work_flow/run.py` → `modules/*/core`**；改 `_company` 內 JSON/YAML 先動 [`schemas/documents.py`](design/src-layout.md)。

### 如何閱讀

| 用語 | 意思 |
|------|------|
| **架構軌 A0–A1** | `src/` 分層、模組遷移（與 CEO／PM 功能可並行） |
| **產品軌 P-A1–P-A3** | Harness 優先序 Phase A：CEO 全公司 → PM 建局 → PM Git／維修 |
| **建殼** | CEO：新專案 id、目錄、`projects.json`、PM session 索引；**不**寫 Worker 編制（§六） |
| **建局** | PM：編制、`workers/<id>/`、專案 skill、對話、狀態查詢（§七） |
| **P-A1+** | 已併入 §六 的建殼、CEO Session、global skill（§二表僅留對照） |

各產品章（§六起）標題寫 **能力**；代號與 harness 章節放在章首或對照表（§十四）。

| 章節類型 | 標題後綴 |
|----------|----------|
| 交付章（§四–§十二，勾選已齊） | `（已完成）` |
| 流程／對照／速查（§一、§二、§十三、§十四） | `（參考）` |
| 現況表（§三） | `（現況 · 日期）` |
| 技術債表（§十五） | `（主項已收斂）` |

---

## 一、每次開發的標準步驟（參考）

適用於新指令、新 flow、新模組或改契約。

| 步驟 | 要做的事 | 產物／檢查 |
|------|----------|------------|
| 1 | 對照 harness：屬 **CEO 全公司** 還是 **PM 單專案**？ | 在 harness-design 找到對應章節 |
| 2 | 定義 **Command / Result**（必要時 **Document DTO**） | `schemas/commands.py`、`results.py`、`documents.py` |
| 3 | 新增 **`<slug>__work_flow/run.py`**：`run` + `register` | 目錄 `README.md`（中文一句話） |
| 4 | 在 **`work_flow/_register.py`** 登記 | `registry.list_flows()` 可見 |
| 5 | **通道**掛載：TG / CLI /（後期）Web | 更新 `adapters/README.md` 路由表 |
| 6 | 業務 I/O 只經 **工具模組 `core`** | flow 不 import `internal/`；handler 見 skill 過渡期 |
| 7 | **測試**：flow 整合 + 模組單元 | `pytest` |
| 8 | **文件**：本檔勾選、`document-audit` 若改契約則更新 | PR 自檢 |

過渡期：`on_text` 經 **`RouteManagerChatCommand`** → `route_manager_chat__work_flow`（見 §十五 #2）；**新指令**仍須 `dispatch` + flow。

**§一 與現況**

| 步驟 | 狀態 |
|------|------|
| 5 `adapters/README.md` 路由表 | 完成（TG／CLI／Web 對照 `Command`） |
| 8 `harness-design` §10 核取 | 已回寫；**執行勾選以本檔為準**（§十四） |

---

## 二、雙軌階段對照（參考）

**產品軌**（harness 優先序）與 **架構軌**（src-layout）並行；同一時期可能兩邊都有勾選項。

| 順序 | 架構軌 | 產品軌（白話） | 本檔 |
|------|--------|----------------|------|
| 0 | **A0** 分層骨架 | — | §四 |
| 1 | **A1** 工具模組遷移 | **P-A1** CEO：列表、建殼、全公司 skill／設定、CEO 對話 | §五、§六 |
| 2 | — | **P-A1+**（併入 §六） | §六 2–5 |
| 3 | — | **P-A2** PM：編制、專案 skill、對話、狀態查詢 | §七 |
| 4 | — | **P-A3** PM：沙盒 Git、維修、TG 核准 | §八 |
| 5 | `execution_store`、`sandbox_runner` | **B** 狀態機、排程、執行者通知 | §九 |
| 6 | — | **B+** Skill 生態（registry 與啟用 flow） | §十 |
| 7 | 網頁 adapter | **C** 端到端 QA 閉環 | §十一 |
| 8 | — | **二期** COO 報表、Web 產品化、評分 | §十二 |

**§二 產品與架構主線（順序 0–8）均已交付**；後續為能力擴充（真實 Worker、Web 安全硬化等），見優化 backlog 或新 Phase 章節。

---

## 三、現況快照（現況 · 2026-06-24）

| 項目 | 狀態 |
|------|------|
| 架構 **A0**、**A1**（§四、§五） | 完成 |
| **P-A1** CEO 全公司（§六） | 完成 |
| **P-A2** PM 編制／skill／對話／狀態（§七） | 完成 |
| **P-A3** Git／維修／TG 核准（§八） | 完成 |
| **B**／**B+**／**C**（§九–§十一） | 完成 |
| **第二期** COO／Web／評分（§十二） | 完成 |
| `work_flow` 已註冊 **23** 條 `run.py` flow | 完成 |
| `adapters/telegram`、`adapters/cli`、`adapters/web` → `dispatch` | 完成 |
| **模擬驗收**（§十三 表） | 完成（含 `simulate_common` 離線 deps） |
| **架構收斂**（§十五 #1–3） | **完成** |
| TG：`/global`、`/updateglobal`、`/removeskill` | 完成 |

---

## 四、架構 A0 — 分層骨架（已完成）

建立 `work_flow` + `dispatch` + `schemas` 骨架與文件，讓後續功能一律走 flow。

- [x] `docs/design/src-layout.md`、Cursor rules、`ai-ceo-framework` skill
- [x] `work_flow/registry.py`、Phase A 初版四 flow（`run.py`）
- [x] `schemas/`、`adapters/dispatch.py`
- [x] 過渡期與 `telegram/` 路徑說明文件化

**驗收**：`.venv/bin/pytest` 全綠；`./run.sh` / `main init-workspace` 與 list/switch/global 行為正常。

**§四 備註**：「Phase A 四 flow」為 A0 當時表述；現以 §三 flow 總數（23）為準。

---

## 五、架構 A1 — 工具模組與遺留刪除（已完成）

| # | 要做的事 | 驗收 |
|---|----------|------|
| 1 | 集中檔案 I/O：`modules/file_store` | `tests/modules/test_file_store*.py` |
| 2 | 工作區初始化：`modules/setup_workspace` | `init_workspace__work_flow` |
| 3 | 專案目錄與建殼編排：`setup_project_folders` | `create_project_shell`；專案 YAML 經 `file_store` |
| 4 | flow 僅呼叫 `modules.*.core` | 無 `legacy_services` |
| 5 | Telegram 適配層遷移 | `adapters/telegram/`、`router` |
| 6 | 刪除舊層；CLI 遷至 `adapters/cli` | 無 `store/`、`services/` |

- [x] 步驟 1–6

**§五 備註**：§十五 #1 **模組依賴收斂**不推翻 A1 勾選。

---

## 六、產品 P-A1 — CEO：專案與全公司設定（已完成）

**代號**：P-A1 · **規格錨點**：[`harness-design.md`](design/harness-design.md) §2.2 優先序第 1 項。

CEO 動作影響 **所有專案**（或建立新專案 **殼**）。PM 專案內建局見 §七。

| # | 步驟（做什麼） | 架構產物 | 驗收 |
|---|----------------|----------|------|
| 1 | **查詢／切換** active 專案；**查詢**全公司 global 設定摘要 | `list_projects__work_flow`、`switch_project__work_flow`、`show_global_config__work_flow` | TG + CLI 行為一致 |
| 2 | **建立** 新專案殼（id、目錄、索引、PM session 索引） | `create_project__work_flow` | 失敗回滾；**不**寫 `workers.yaml` |
| 3 | **對話**：CEO Session + 全公司脈絡 chat | `ceo_chat__work_flow`、`ai_core`、`file_store` sessions | Fake 或 Gemini 可對話 |
| 4 | **寫入** 全專案啟用的 registry skill（`global_skills`） | `add_skill_to_company__work_flow` | 僅 CEO flow |
| 4b | **移除** 全公司已啟用 skill | `remove_skill_from_company__work_flow` | TG／CLI |
| 5 | **寫入** 全公司預設（模型、通知、AI 參數） | `update_global_config__work_flow` | 與 `ai_core.resolve_model` 銜接 |

- [x] 步驟 1–5、4b

**驗收**：`scripts/simulate_p_a1_acceptance.py`；建殼失敗回滾見 `tests/work_flow/test_create_project_flow.py`。

---

## 七、產品 P-A2 — PM：編制、專案 skill、對話與狀態查詢（已完成）

**代號**：P-A2 · **規格錨點**：[`harness-design.md`](design/harness-design.md) §2.2 優先序第 2 項（不含 Git／維修，見 §八）。

**建殼 vs 建局**：§六 CEO **建殼**只建立專案 id 與目錄骨架，**不**寫 Worker 編制。本章是 PM 在 **單一 `active_project_id`** 內 **建局**——宣告要有哪些 Worker、啟用哪些專案級 skill、與模型對話、**唯讀**查看現況。編制與各 Worker 目錄是 Phase B 派工與 `ToolPolicy` 沙盒的前置（見 harness §5）。

| # | 步驟（做什麼） | 架構產物 | 驗收 |
|---|----------------|----------|------|
| 1 | **切換／綁定** PM mode：指令只作用在目前 active 專案 | `set_user_mode__work_flow` 等；Command 帶 `project_id` | TG／CLI 路由正確 |
| 2 | **對話**：PM 專案 chat + 每專案 Session 持久化 | `pm_chat__work_flow`、`file_store` + `ai_core` | `sessions/pm_<id>.json` |
| 3 | **寫入** Worker 編制表並 **建立** 各角色工作目錄（派工與工具邊界前置） | `setup_workers__work_flow` → `workers.yaml`、`workers/<id>/` | 自訂 `kind` 須有 `SKILL.md` |
| 4 | **寫入** 本專案全角色共用的 registry skill 清單 | `add_skill_to_project__work_flow` → `project_skills.yaml` | id 與 `skills/registry/` 對齊 |
| 5 | **查詢（唯讀）** 專案現況：`shared/`、`pm/`、編制、專案 skill | `show_project_status__work_flow` | 不修改沙盒檔案 |

- [x] 步驟 1–5

---

## 八、產品 P-A3 — PM：沙盒 Git、維修與 TG 核准（已完成）

**代號**：P-A3 · **規格錨點**：harness §2.2 第 2 項之 **Git、維修**（與 §七 建局分章，便於驗收 ToolPolicy 與人機關卡）。

| # | 步驟（做什麼） | 架構產物 | 驗收 |
|---|----------------|----------|------|
| 1 | **執行** 專案沙盒內 Git（路徑限 `projects/<id>/`） | `project_git__work_flow` + ToolPolicy 預檢 | 越界拒絕 |
| 2 | **閘道**：高風險 Git／專案 skill 安裝須 TG Inline **核准**後才執行 | `resolve_approval__work_flow`、pending 佇列 | 未核准不執行 |
| 3 | **查詢／介入** 維修摘要；可 **手動中斷** execution（與未來 §九 佇列協同） | `pm_repair__work_flow` | 可先不依完整狀態機 |

- [x] 步驟 1–3

---

## 九、產品 B — 執行層：佇列、沙盒執行、排程與通知（已完成）

**代號**：B · **規格錨點**：harness §2.2 第 3 項、§7 反饋層。

在 §七 建局完成後，**一次一個 Worker** 在沙盒內執行；失敗時經 TG 請人決策（重試／code review）。

| # | 步驟（做什麼） | 模組／flow | 驗收 |
|---|----------------|------------|------|
| 1 | **持久化** 全公司單一執行佇列（取代 `worker_state`） | `execution_store`、`execution/*.json` | 可恢復（**core 空殼已有**，§十五） |
| 2 | **執行** 子程序／工具：cwd 與路徑受 ToolPolicy 限制 | `sandbox_runner` + worker／scheduler flow | 僅允許沙盒內路徑 |
| 3 | **排程** 下一個 Worker（專案內 `task_scheduler` 語意） | `task_scheduler` | 可派工到編制中的 id |
| 4 | **通知** 進度與失敗（執行者 Bot，與管理者 Bot 分離） | `modules/notify` | 文案含 `project_id` |
| 5 | **人機關卡**：失敗時 TG 選重試或 code review | human-in-the-loop flow | harness §7 |
| 6 | **追加（唯寫 log）** 派工與失敗記錄 | `pm/scheduler_decisions.jsonl` | 不做結構化評分門檻 |

- [x] 步驟 1–6

---

## 十、產品 B+ — Skill 生態（已完成）

**代號**：B+ · **規格錨點**：harness §2.2 第 4 項、§5.4 疊加順序。

- [x] **對齊** `skills/registry/` 與 CEO／PM **啟用** flow 的疊加順序（global → project → role）
- [x] **adapter**：find-skills / create-skill（給 **開發本框架** 用；≠ 沙盒內 Worker skill 目錄）

---

## 十一、產品 C — 端到端 QA 閉環（已完成）

**代號**：C · **規格錨點**：harness §2.2 第 5 項。

- [x] QA Worker 產出回流，專案狀態可至 `PROJECT_DONE`（見 harness 測試 Phase B/C）

---

## 十二、第二期（已完成）

- [x] **COO**：`metrics/usage.jsonl`、報表
- [x] **Web 通道**：`adapters/web` + 同一 `dispatch`
- [x] **評分**：結構化 AI 任務評分接入排程閘道（harness §7.2）

---

## 十三、驗收指令速查（參考）

**互動**：`./run.sh` → **3 測試** → **1**（pytest + 下表全部模擬）或 **7**（僅模擬）。

| 路線圖 | 模擬腳本 |
|--------|----------|
| §六 P-A1 | `scripts/simulate_p_a1_acceptance.py` |
| §七 P-A2 | `scripts/simulate_p_a2_acceptance.py` |
| §八 P-A3 | `scripts/simulate_p_a3_acceptance.py` |
| §九–§十一 B／B+／C | `scripts/simulate_p_b_c_acceptance.py` |
| §十二 第二期 | `scripts/simulate_phase2_acceptance.py` |
| **一鍵全部模擬** | `scripts/simulate_all_acceptance.py` |

```bash
# 單元測試
.venv/bin/pytest -q

# 全部模擬（與 run.sh 測試選單 7 相同）
.venv/bin/python scripts/simulate_all_acceptance.py

# Web（或 ./run.sh → 4）
python -m ai_company.adapters.web --port 8765

# 已註冊 flow
.venv/bin/python -c "from ai_company.work_flow import _register; from ai_company.work_flow.registry import registry; print([f.flow_id for f in registry.list_flows()])"

# 本機選單
./run.sh
```

模擬腳本一律經 **`scripts/simulate_common.make_deps`**（Fake chat、不讀 `.env` API key），可離線簽收。

---

## 十四、與 harness-design 測試清單的對應（參考）

| harness-design §10 | 本路線圖 |
|--------------------|----------|
| Phase A（CEO 建殼 + PM 建局與 P-A3） | §五–§八（P-A1、P-A2、P-A3 + 架構 A1） |
| Phase B（Harness 執行） | §九 B |

完成各節勾選後，可回寫 harness-design §10 核取方塊，或 **僅以本檔為執行勾選、harness 為規格**（避免雙處維護）。

---

## 十五、架構技術債與後續收斂（主項已收斂）

P-A1–P-A3 與一輪產品交付已完成；下列為 **刻意保留的過渡實作**，開 Phase B 前請對照 [`src-layout.md`](design/src-layout.md) 依賴規則。

| # | 項目 | 現狀 | 建議修改方向 | 狀態 |
|---|------|------|--------------|------|
| 1 | **`setup_workspace` ↔ `file_store`** | `ensure_workspace` 僅遷移；索引由 `work_flow/_shared/company_workspace` 編排 | `init_workspace`／CEO flow 呼叫 `ensure_company_workspace` | **完成** |
| 2 | **TG `on_text` 直讀 `get_user_mode`** | 改為 `RouteManagerChatCommand` → `route_manager_chat__work_flow` | 單一 dispatch 路由 chat | **完成** |
| 3 | **`worker_state.py`** | 已廢止 | 使用 `execution_store` | **完成** |
| 4 | **Phase B 模組** | 已實作 | §九 | **完成** |

**後續產品（新 Phase，非本檔未完成項）**

- **執行層 v2**：見 [`design/execution-layer-v2.md`](design/execution-layer-v2.md)（先 **E1 backend Worker**，再 scheduler v2／PM 進階）。
- 其他：Web 認證白名單、執行佇列檔案鎖等——見 code review／優化 backlog。

---

## 十六、執行層 v2（E1 — backend Worker）

**規格**：[`design/execution-layer-v2.md`](design/execution-layer-v2.md)  
**預設模板**：[`worker_default/`](../worker_default/README.md)

| # | 步驟 | 驗收 |
|---|------|------|
| 1 | 任務契約（輸入 YAML／輸出 `last_run.json`）定稿並寫入文件 | 與 E3 scheduler 接口一致 |
| 2 | 建立 **`worker_default/backend/`**（`SKILL.md`、`role_skills.yaml`） | 與 §4.0、§4.6 一致 |
| 3 | `skills/registry/` 新增 E1 backend 共用 skill（§4.4）並寫入 `role_skills.yaml` | id 對齊、可 resolve |
| 4 | **`tests/`**：fixture 專案從 worker_default 種子複製 → 跑 backend runner | 不依賴 Training／TG |
| 5 | ToolPolicy：`backend` 測試／lint argv 白名單 | 越界拒絕 |
| 6 | `run-step` 對 `kind=backend` 接 Gemini + 工具（非僅標記） | 測試通過才 DONE |
| 7 | 可選：Training（`d668c955`）小 API 手動端到端 | 碼 + 測試 + `shared/api_docs/` |

- [x] 步驟 1（見 execution-layer-v2 §4.2）
- [x] 步驟 2（目錄與預設 backend 正文；見 `worker_default/`）
- [ ] 步驟 3–7

**刻意延後（E3／E4）**：AI 決定 pipeline、執行期自動 find/install skill、scheduler 主導 code review。  
**`/addworker`**：已實作（E4 部分提前）；與 E-P 種子複製並存，resync 見 §十七。

---

## 十七、執行層 E-P — 三沙盒 Package

**規格**：[`design/worker-sandbox-packages.md`](design/worker-sandbox-packages.md)  
**計畫**：[`plans/phase-e-worker-packages.md`](plans/phase-e-worker-packages.md)

| # | 步驟 | 驗收（pytest／腳本） |
|---|------|----------------------|
| E-P0 | 文件與決策 | 本檔 §十六與 worker-sandbox-packages 一致 |
| E-P1 | 種子 `worker_manifest.yaml` + 各 `package/` 骨架；擴充 copy | `test_worker_default_install` + `test_worker_package_layout` |
| E-P2 | `worker_host` + backend entrypoint | `test_worker_host_backend`、`test_backend_worker_scripted` |
| E-P3 | scheduler 邏輯遷入 scheduler package | scheduler 相關 tests |
| E-P4 | fixtures package 載入場景 | `test_fixtures_package` |
| E-P5 | PM resync + repair 健檢 | `test_pm_resync_worker_flow`、`test_pm_repair_flow` |
| E-P6 | `run-step` → worker_host | `test_run_execution_step_flow`、全量 `pytest` |

- [x] E-P0（文件）
- [x] E-P1–E-P6（見 commit；`pytest` 109 passed）
