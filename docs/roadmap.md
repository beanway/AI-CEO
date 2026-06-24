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

---

## 一、每次開發的標準步驟（不論 Phase）

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

過渡期：`manager_handlers.on_text` 可暫用 **`file_store.get_user_mode`** 決定 CEO／PM chat（見 §十五）；**新指令**仍須 `dispatch` + flow。

**§一 與現況（未當成 Phase 勾選，但常漏）**

| 缺口 | 為何未做 | 何時可做 |
|------|----------|----------|
| 步驟 5：`adapters/README.md` 路由表未列齊 TG／CLI | 產品迭代快於文件；不擋 dispatch | 下一個改 adapter 或補 TG 指令的 PR 順手更新 |
| 步驟 8：`harness-design` §10 核取未回寫 | §十四 約定 **以本檔為執行勾選** | 需要對外簽收 Phase A 時回寫，或維持單一真相在本檔 |

---

## 二、雙軌階段對照

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

**§二 尚未進行的列（順序 5–8）**：需 §七 建局與（部分）執行層就緒；**刻意排在 P-A1–P-A3 之後**，避免無沙盒／無 ToolPolicy 時先做排程。對照 §九–§十二 勾選項。

---

## 三、現況快照（2026-06-24）

| 項目 | 狀態 |
|------|------|
| 架構 **A0**、**A1**（§四、§五） | 完成 |
| **P-A1** CEO 全公司（§六） | 完成 |
| **P-A2** PM 編制／skill／對話／狀態（§七） | 完成 |
| **P-A3** Git／維修／TG 核准（§八） | 完成 |
| `work_flow` 已註冊 **20** 條 `run.py` flow | 完成 |
| `modules`：`file_store`、`setup_workspace`、`setup_project_folders`、`format_messages`、`ai_core`、`settings`、`skill_registry` | 完成（CEO／全公司與 PM 路徑） |
| `adapters/telegram`、`adapters/cli` → `dispatch` | 完成 |
| 已刪 `services/`、`store/`、`workspace.py`、`legacy_services` | 完成 |
| TG：`/projects`、`/switch`、`/newproject`、`/addskill`、`/mode`、`/setupworkers`…；`on_text` 依 mode → **`ceo_chat` / `pm_chat`** | 完成 |
| CLI：對等子命令（`mode`、`pm-chat`、`setup-workers`、`project-status` 等） | 完成 |
| **架構收斂**（§十五 #1–2） | **待做** |
| **B** 執行層（§九：`execution_store` 佇列、`task_scheduler`） | **完成** |

**§三 未完成項（為何／何時）**

| 項目 | 為何未做 | 何時可做 |
|------|----------|----------|
| **架構收斂**（§十五 #1–2） | Phase A 先交付產品；`on_text` 直讀 mode、`setup_workspace`↔`file_store` 為過渡取捨 | **Phase B 前**小步 PR（§十五 表） |
| **B 執行層** | 佇列與排程屬 §九；Git／核准已於 P-A3 交付 | **§九** |

---

## 四、架構 A0 — 分層骨架（已完成）

建立 `work_flow` + `dispatch` + `schemas` 骨架與文件，讓後續功能一律走 flow。

- [x] `docs/design/src-layout.md`、Cursor rules、`ai-ceo-framework` skill
- [x] `work_flow/registry.py`、Phase A 初版四 flow（`run.py`）
- [x] `schemas/`、`adapters/dispatch.py`
- [x] 過渡期與 `telegram/` 路徑說明文件化

**驗收**：`.venv/bin/pytest` 全綠；`./run.sh` / `main init-workspace` 與 list/switch/global 行為正常。

**§四 備註**：「Phase A 四 flow」為 A0 當時表述；現以 §三 flow 總數（16）為準。

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

## 六、產品 P-A1 — CEO：專案與全公司設定

**代號**：P-A1 · **規格錨點**：[`harness-design.md`](design/harness-design.md) §2.2 優先序第 1 項。

CEO 動作影響 **所有專案**（或建立新專案 **殼**）。PM 專案內建局見 §七。

| # | 步驟（做什麼） | 架構產物 | 驗收 |
|---|----------------|----------|------|
| 1 | **查詢／切換** active 專案；**查詢**全公司 global 設定摘要 | `list_projects__work_flow`、`switch_project__work_flow`、`show_global_config__work_flow` | TG + CLI 行為一致 |
| 2 | **建立** 新專案殼（id、目錄、索引、PM session 索引） | `create_project__work_flow` | 失敗回滾；**不**寫 `workers.yaml` |
| 3 | **對話**：CEO Session + 全公司脈絡 chat | `ceo_chat__work_flow`、`ai_core`、`file_store` sessions | Fake 或 Gemini 可對話 |
| 4 | **寫入** 全專案啟用的 registry skill（`global_skills`） | `add_skill_to_company__work_flow` | 僅 CEO flow |
| 5 | **寫入** 全公司預設（模型、通知、AI 參數） | `update_global_config__work_flow` | 與 `ai_core.resolve_model` 銜接 |

- [x] 步驟 1–5

**§六 主幹已完成；介面／次要路徑未齊（不推翻上列勾選）**

| 缺口 | 為何未做 | 何時可做 |
|------|----------|----------|
| 步驟 1：TG 無 `/global` | MVP 先 CLI `global`；列表／切換已在 TG | 補 TG 路由的小 PR |
| 步驟 2：建殼 **回滾** 無專門 pytest | 成功路徑已驗 | 隨時補測試 |
| 步驟 4：無 **移除** global skill 的 flow | 可手改 YAML；新增已覆蓋主路徑 | 營運需要或併入 **B+** |
| 步驟 5：TG 無 `update-global` | 變更頻率低；CLI + flow 已有 | 與 `/global` 同一輪或維持 YAML |
| §一 步驟 5：`adapters/README` 未列全 CEO 指令 | 見 §一 表 | 與 TG 補指令同 PR |

---

## 七、產品 P-A2 — PM：編制、專案 skill、對話與狀態查詢

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

## 八、產品 P-A3 — PM：沙盒 Git、維修與 TG 核准

**代號**：P-A3 · **規格錨點**：harness §2.2 第 2 項之 **Git、維修**（與 §七 建局分章，便於驗收 ToolPolicy 與人機關卡）。

| # | 步驟（做什麼） | 架構產物 | 驗收 |
|---|----------------|----------|------|
| 1 | **執行** 專案沙盒內 Git（路徑限 `projects/<id>/`） | `project_git__work_flow` + ToolPolicy 預檢 | 越界拒絕 |
| 2 | **閘道**：高風險 Git／專案 skill 安裝須 TG Inline **核准**後才執行 | `resolve_approval__work_flow`、pending 佇列 | 未核准不執行 |
| 3 | **查詢／介入** 維修摘要；可 **手動中斷** execution（與未來 §九 佇列協同） | `pm_repair__work_flow` | 可先不依完整狀態機 |

- [x] 步驟 1–3

---

## 九、產品 B — 執行層：佇列、沙盒執行、排程與通知

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

## 十、產品 B+ — Skill 生態

**代號**：B+ · **規格錨點**：harness §2.2 第 4 項、§5.4 疊加順序。

- [x] **對齊** `skills/registry/` 與 CEO／PM **啟用** flow 的疊加順序（global → project → role）
- [x] **adapter**：find-skills / create-skill（給 **開發本框架** 用；≠ 沙盒內 Worker skill 目錄）

---

## 十一、產品 C — 端到端 QA 閉環

**代號**：C · **規格錨點**：harness §2.2 第 5 項。

- [x] QA Worker 產出回流，專案狀態可至 `PROJECT_DONE`（見 harness 測試 Phase B/C）

---

## 十二、第二期

- [ ] **COO**：`metrics/usage.jsonl`、報表
- [ ] **Web 通道**：`adapters/web` + 同一 `dispatch`
- [ ] **評分**：結構化 AI 任務評分接入排程閘道（harness §7.2）

---

## 十三、驗收指令速查

```bash
# 測試
.venv/bin/pytest -q

# 已註冊 flow
.venv/bin/python -c "from ai_company.work_flow import _register; from ai_company.work_flow.registry import registry; print([f.flow_id for f in registry.list_flows()])"

# 本機 CEO CLI
./run.sh
```

---

## 十四、與 harness-design 測試清單的對應

| harness-design §10 | 本路線圖 |
|--------------------|----------|
| Phase A（CEO 建殼 + PM 建局與 P-A3） | §五–§八（P-A1、P-A2、P-A3 + 架構 A1） |
| Phase B（Harness 執行） | §九 B |

完成各節勾選後，可回寫 harness-design §10 核取方塊，或 **僅以本檔為執行勾選、harness 為規格**（避免雙處維護）。

---

## 十五、架構技術債與後續收斂（Phase A 交付後）

P-A1–P-A3 與一輪產品交付已完成；下列為 **刻意保留的過渡實作**，開 Phase B 前請對照 [`src-layout.md`](design/src-layout.md) 依賴規則。

| # | 項目 | 現狀 | 建議修改方向 | 建議時機 |
|---|------|------|--------------|----------|
| 1 | **`setup_workspace` ↔ `file_store`** | `ensure_workspace` 內直接呼叫 `file_store.ensure_company_*` | 由 **`init_workspace__work_flow`**／啟動路徑編排；避免模組互引 `core` | Phase B 前小步 PR |
| 2 | **TG `on_text` 直讀 `get_user_mode`** | `manager_handlers` 未經 `dispatch` 分支 CEO／PM chat | **`route_manager_chat__work_flow`**（或等價單一 Command）；更新 framework skill 過渡說明 | Phase B 前（§三 待做） |
| 3 | **`worker_state.py`** | 固定五角色佔位；已標廢止 | 遷移至 **`execution_store`**（§九 步驟 1） | §九 步驟 1 |
| 4 | **Phase B 模組空殼** | `execution_store`、`sandbox_runner`、`notify` 僅骨架 | 依 §九 實作 | P-A3 之後；Git 深化可與 `sandbox_runner` 並行 |

**下一步產品優先序**

- **Phase B**（§九）：佇列、`task_scheduler`、執行者通知；銜接 harness §7 失敗決策。
- 架構收斂（上表 #1–2）可與 §九 第一個 flow **同輪小 PR**，不擋排程主線。

**驗收（收斂項）**

- `rg 'from ai_company.modules.file_store' src/ai_company/modules/setup_workspace` 無 `core` 互依，或已文件化例外並有 flow 編排。
- `manager_handlers.on_text` 僅 `dispatch` 一條 chat 路由 Command。
- `.venv/bin/pytest -q` 全綠。
