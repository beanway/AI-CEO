# 實作路線圖

**角色**：本檔是 **「做什麼、先做什麼、怎麼驗收」** 的總表；細節規格見下表。

| 主題 | 文件 |
|------|------|
| 產品／CEO·PM·Worker | [`design/harness-design.md`](design/harness-design.md) |
| 程式分層、modules、work_flow | [`design/src-layout.md`](design/src-layout.md) |
| A1 模組遷移拆解 | [`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md) |
| 共識摘要 | [`discussion-outcomes.md`](discussion-outcomes.md) |

**原則**：新能力一律 **Command → `adapters.dispatch` → `*__work_flow/run.py` → `modules/*/core`**；改 `_company` 內 JSON/YAML 先動 [`schemas/documents.py`](design/src-layout.md)。

---

## 一、每次開發的標準步驟（不論 Phase）

適用於新指令、新 flow、新模組或改契約。

| 步驟 | 動作 | 產物／檢查 |
|------|------|------------|
| 1 | 對照 harness：屬 **CEO 全公司** 還是 **PM 單專案**？ | 在 harness-design 找到對應章節 |
| 2 | 定義 **Command / Result**（必要時 **Document DTO**） | `schemas/commands.py`、`results.py`、`documents.py` |
| 3 | 新增 **`<slug>__work_flow/run.py`**：`run` + `register` | 目錄 `README.md`（中文一句話） |
| 4 | 在 **`work_flow/_register.py`** 登記 | `registry.list_flows()` 可見 |
| 5 | **通道**掛載：TG / CLI /（後期）Web | 更新 `adapters/README.md` 路由表 |
| 6 | 業務 I/O 只經 **工具模組 `core`** | flow 不 import `internal/`；handler 見 skill 過渡期 |
| 7 | **測試**：flow 整合 + 模組單元 | `pytest` |
| 8 | **文件**：`roadmap` 勾選、`document-audit` 若改契約則更新 | PR 自檢 |

過渡期：`manager_handlers.on_text` 可暫用 **`file_store.get_user_mode`** 決定 CEO／PM chat（見 §十五）；新指令仍須 `dispatch` + flow。

**§一 與現況（未當成 Phase 勾選，但常漏）**

| 缺口 | 為何未做 | 何時可做 |
|------|----------|----------|
| 步驟 5：`adapters/README.md` 路由表未列齊 TG／CLI | 產品迭代快於文件；不擋 dispatch | 下一個改 adapter 或補 TG 指令的 PR 順手更新 |
| 步驟 8：`harness-design` §10 核取未回寫 | §十四 約定 **以本檔為執行勾選** | 需要對外簽收 Phase A 時回寫，或維持單一真相在本檔 |

---

## 二、雙軌階段對照

**產品軌**（harness 優先序）與 **架構軌**（src-layout）並行；同一時期可能兩邊都有勾選項。

| 順序 | 架構軌 | 產品軌（Harness） | 依賴 |
|------|--------|-------------------|------|
| 0 | **A0** 分層骨架 | — | — |
| 1 | **A1** 工具模組遷移 | **P-A1** CEO 全公司（§六 已完成） | A0 |
| 2 | — | **P-A1+** 建殼、CEO Session、global skill | 已完成（併入 §六 2–5） |
| 3 | — | **P-A2** PM 建局 | A1 |
| 4 | — | **P-A3** PM Git／維修／TG 核准 | P-A2 |
| 5 | `execution_store`、`sandbox_runner` | **B** 狀態機、scheduler、notify | P-A2 |
| 6 | — | **B+** Skill 生態 | B 骨架 |
| 7 | 網頁 adapter | **C** QA 閉環 | B |
| 8 | — | **二期** COO、評分、Web 產品化 | C |

**§二 尚未進行的列（順序 4–8）**：依賴 P-A2 殼局與（部分）執行層；**刻意排在 P-A1／P-A2 之後**，避免在無沙盒／無 ToolPolicy 時先做 Git 或排程。對照 §八–§十二 勾選項。

---

## 三、現況快照（2026-06-23）

| 項目 | 狀態 |
|------|------|
| 架構 **A0**、**A1** | 完成 |
| **P-A1** CEO 全公司（§六 步驟 1–5） | 完成 |
| `work_flow` 已註冊 **13** 條 `run.py` flow | 完成 |
| `modules`：`file_store`、`setup_workspace`、`setup_project_folders`、`format_messages`、`ai_core`、`settings`、`skill_registry` | 完成（CEO／全公司路徑） |
| `adapters/telegram`、`adapters/cli` → `dispatch` | 完成 |
| 已刪 `services/`、`store/`、`workspace.py`、`legacy_services` | 完成 |
| TG：`/projects`、`/switch`、`/newproject`、`/addskill`、`/mode`、`/setupworkers`…；`on_text` 依 mode → **`ceo_chat` / `pm_chat`** | 完成 |
| CLI：對等子命令 + PM（`mode`、`pm-chat`、`setup-workers`、`project-status` 等） | 完成 |
| **P-A2** PM 建局（mode 路由、`pm_chat`、`workers.yaml`、`project_skills`、狀態 flow） | **完成** |
| **架構收斂**（§十五）：`setup_workspace`↔`file_store`、`on_text` 直讀 mode | **待做** |
| **P-A3** Git／維修／TG 核准；**B** 執行層（`execution_store` 實作） | 未做 |

**§三 未完成項（為何／何時）**

| 項目 | 為何未做 | 何時可做 |
|------|----------|----------|
| **架構收斂**（§十五 #1–2） | P-A2 先交付產品；`on_text` 直讀 mode、`setup_workspace`↔`file_store` 為過渡取捨 | **P-A3 前**或與 P-A3 第一個 flow 同 PR（§十五 表） |
| **P-A3** | 需 ToolPolicy、沙盒 Git、TG Inline 核准設計 | P-A2 完成後 **§八** 依序 |
| **B 執行層** | 依賴 PM 編制與（建議）P-A3 邊界；`execution_store` 現為空殼 | **§九**；可與 P-A3 並行，Git 路徑需時優先 `sandbox_runner` |

---

## 四、架構 A0 — 分層骨架（已完成）

- [x] `docs/design/src-layout.md`、Cursor rules、`ai-ceo-framework` skill
- [x] `work_flow/registry.py`、Phase A 四 flow（`run.py`）
- [x] `schemas/`、`adapters/dispatch.py`
- [x] 過渡期與 `telegram/` 路徑說明文件化

**驗收**：`.venv/bin/pytest` 全綠；`./run.sh` / `main init-workspace` 與 list/switch/global 行為正常。

**§四 未完成項**：無（步驟均已勾選）。文中「Phase A 四 flow」為 A0 當時表述；現以 §三 flow 總數為準，不另開架構票。

---

## 五、架構 A1 — 工具模組與遺留刪除（已完成）

| # | 步驟 | 驗收 |
|---|------|------|
| 1 | `modules/file_store` | `tests/modules/test_file_store*.py` |
| 2 | `modules/setup_workspace` | `init_workspace__work_flow` |
| 3 | `modules/setup_project_folders` | 建殼編排在 `create_project_shell`；專案 YAML 經 `file_store` |
| 4 | flow 僅用 `modules.*.core` | 無 `legacy_services` |
| 5 | `adapters/telegram/` | `router` 已切換 |
| 6 | 刪除舊層；`ceo_cli` → `adapters/cli` | 無 `store/`、`services/` |

- [x] 步驟 1–6

**§五 未完成項**：無。模組遷移與舊層刪除已驗收；後續僅 §十五 #1 的 **模組依賴收斂**（不影響 A1 勾選語意）。

---

## 六、產品 P-A1 — CEO 全公司（Harness §2.2 第 1 項）

| # | 步驟 | 架構產物 | 驗收 |
|---|------|----------|------|
| 1 | 專案列表／切換／顯示 global | 既有四 flow | TG + CLI 一致 |
| 2 | **建專案殼**（id、目錄、索引、PM session 索引） | `create_project__work_flow/run.py` | 失敗回滾；不寫 Worker 編制 |
| 3 | **`modules/ai_core`** + CEO Session 持久化（`file_store` sessions） | `ceo_chat__work_flow`（名稱可調） | Fake 或 Gemini 可對話 |
| 4 | 讀寫 **global_skills**（CEO） | `add_skill_to_company__work_flow` | 僅 CEO flow；TG 可先 YAML |
| 5 | **global_config** 變更（模型、通知政策） | 對應 Command + flow | 與 `ai_core.resolve_model` 銜接 |

- [x] 步驟 1（列表／切換／global 展示）
- [x] 步驟 2（建專案殼）
- [x] 步驟 3（CEO Session + `ceo_chat__work_flow`）
- [x] 步驟 4（`add_skill_to_company__work_flow`）
- [x] 步驟 5（`update_global_config__work_flow` + AI 欄位）

**§六 主幹已完成；下列為驗收欄／介面未齊（不推翻上列勾選）**

| 缺口 | 為何未做 | 何時可做 |
|------|----------|----------|
| 步驟 1：TG 無 `/global`（global 展示僅 CLI `global`） | MVP 先打通 flow + CLI；列表／切換已在 TG | **P-A1 補齊**小 PR，或下一個動 TG 路由時加 `/global` |
| 步驟 2：建專案 **回滾** 無專門 pytest | `create_project_shell` 已實作回滾；優先驗成功路徑 | 隨時補 **單元／整合測試**（不擋 Phase A 簽收） |
| 步驟 4：**移除** 公司級 `global_skills` 無 flow | 規格允許 **手改 YAML**；新增 skill 已覆蓋主路徑 | 營運需要時加 `remove_skill_from_company__work_flow`，或併入 **B+** skill 管理 |
| 步驟 5：TG 無 `update-global` | 模型／通知政策變更頻率低；CLI + flow 已接 `ai_core` | 同 **TG `/global` 補齊** PR，或維持 CLI／YAML |
| §一 步驟 5：`adapters/README` 未列全 CEO 指令 | 見 §一 表 | 與 TG 補指令同一輪更新 |

---

## 七、產品 P-A2 — PM 單專案建局（Harness §2.2 第 2 項）

| # | 步驟 | 架構產物 | 驗收 |
|---|------|----------|------|
| 1 | PM mode 與 `active_project_id` 綁定 | Command 帶 `project_id` / user mode | TG 路由正確 |
| 2 | PM Session per 專案 | `file_store` + `ai_core` | `sessions/pm_<id>.json` |
| 3 | 寫入 **`workers.yaml`**、建立 **`workers/<id>/`** | `setup_project_folders` + flow | kind 校驗 SKILL |
| 4 | **`project_skills.yaml`** | flow + `file_store` | 與 registry 對齊 |
| 5 | 專案狀態摘要（`pm/`、`shared/`） | `show_project_status__work_flow` | 純讀為主 |

- [x] 步驟 1–5

---

## 八、產品 P-A3 — PM 維修與 Git

| # | 步驟 | 驗收 |
|---|------|------|
| 1 | Git 僅限專案沙盒路徑 | ToolPolicy 預檢 |
| 2 | 高風險 Git / skill 安裝 → **TG Inline 核准** | 未核准不執行 |
| 3 | 維修 flow 與（未來）execution 狀態協同 | 可先手動中斷 |

- [ ] 步驟 1–3

---

## 九、產品 B — Harness 執行層

| # | 步驟 | 模組／flow | 驗收 |
|---|------|------------|------|
| 1 | **`modules/execution_store`** ← `worker_state` + `execution/*.json` | 單一佇列 | 持久化可恢復（**core 空殼已有**，見 §十五） |
| 2 | **`modules/sandbox_runner`** + ToolPolicy | scheduler / worker flow | cwd 限沙盒 |
| 3 | **`task_scheduler`** Worker 排程 | 專案內 Worker 語意 | 下一 Worker 可派工 |
| 4 | **`modules/notify`** + 執行者 Bot | 進度／失敗通知 | 與管理者 Bot 分離 |
| 5 | 失敗 TG：**重試 / code review** | human-in-the-loop flow | harness §7 |
| 6 | `pm/scheduler_decisions.jsonl` | 記錄派工與失敗 | 無結構化評分 |

- [ ] 步驟 1–6

---

## 十、產品 B+ — Skill 生態

- [ ] `skills/registry/` 與 CEO/PM 啟用 flow 對齊 harness §5.4 疊加順序
- [ ] find-skills / create-skill **adapter**（開發框架用，≠ Worker skill 目錄）

---

## 十一、產品 C — 端到端 QA 閉環

- [ ] QA Worker 回流、狀態至 `PROJECT_DONE`（harness 測試 §Phase B/C）

---

## 十二、第二期

- [ ] COO：`metrics/usage.jsonl`、報表
- [ ] **Web 通道**：`adapters/web` + 同一 `dispatch`
- [ ] 結構化 AI 任務評分接入排程

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
| Phase A（CEO+PM 殼局） | P-A1、P-A2 + 架構 A1 |
| Phase B（Harness 執行） | 第九節 B |

完成各節勾選後，可回寫 harness-design §10 核取方塊或僅以本檔為準（避免雙處維護時建議 **以 roadmap 為執行勾選、harness 為規格**）。

---

## 十五、架構技術債與後續收斂（P-A2 之後）

P-A2 與一輪架構收斂（建殼編排、`schemas/documents`、Phase B 模組空殼）已完成；下列項目 **刻意保留或尚未處理**，開發下一階段前請對照 [`src-layout.md`](design/src-layout.md) 依賴規則。

| # | 項目 | 現狀 | 建議修改方向 | 建議時機 |
|---|------|------|--------------|----------|
| 1 | **`modules/setup_workspace` → `modules/file_store`** | `ensure_workspace` 內直接呼叫 `file_store.ensure_company_*` | 改由 **`init_workspace__work_flow`**／`router` 啟動路徑編排兩模組，或抽出共用的 **非 `core` 內部**路徑常數；避免模組互引 `core` | 架構小步（可與 A1 補票併做） |
| 2 | **TG `on_text` 直讀 `file_store.get_user_mode`** | `adapters/telegram/manager_handlers` 未經 `dispatch` 即分支 CEO／PM chat | 新增 **`route_manager_chat__work_flow`**（或 `GetUserMode` + 內部分派），handler 只送 **單一 Command**；更新 `.cursor/skills/ai-ceo-framework` 過渡期說明 | P-A3 前或與 P-A3 第一個 flow 同 PR |
| 3 | **`worker_state.py`** | 固定五角色佔位；已標廢止 | 刪除或遷移邏輯至 **`execution_store`** 實作 | **Phase B** §九 步驟 1 |
| 4 | **Phase B 模組** | `execution_store`、`sandbox_runner`、`notify` 僅空殼 | 依 §九 實作佇列、ToolPolicy、執行者 Bot 通知 | **P-A3** 之後或與 P-A3 並行（Git 需 `sandbox_runner` 時優先） |

**產品優先序（與上表可並行）**

- **P-A3**：專案沙盒 Git、維修 flow、TG Inline 核准（§八）。
- **Phase B**：`execution_store` 持久化與 `task_scheduler` 排程（§九）；與 harness §7 人機關卡銜接。

**驗收（收斂項）**

- `rg 'from ai_company.modules.file_store' src/ai_company/modules/setup_workspace` 無 `core` 互依，或已文件化例外並有 flow 編排。
- `manager_handlers.on_text` 僅 `dispatch` 一條 chat 路由 Command。
- `.venv/bin/pytest -q` 全綠。
