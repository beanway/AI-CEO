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

過渡期：`on_text` 可暫用 `file_store.get_active_project`，見 skill「過渡期例外」。

---

## 二、雙軌階段對照

**產品軌**（harness 優先序）與 **架構軌**（src-layout）並行；同一時期可能兩邊都有勾選項。

| 順序 | 架構軌 | 產品軌（Harness） | 依賴 |
|------|--------|-------------------|------|
| 0 | **A0** 分層骨架 | — | — |
| 1 | **A1** 工具模組遷移 | **P-A1** CEO 列表／切換／global（已部分完成） | A0 |
| 2 | — | **P-A1+** 建殼、CEO Session、global skill | A1 建議先完成 `file_store` |
| 3 | — | **P-A2** PM 建局 | A1 |
| 4 | — | **P-A3** PM Git／維修／TG 核准 | P-A2 |
| 5 | `execution_store`、`sandbox_runner` | **B** 狀態機、scheduler、notify | P-A2 |
| 6 | — | **B+** Skill 生態 | B 骨架 |
| 7 | 網頁 adapter | **C** QA 閉環 | B |
| 8 | — | **二期** COO、評分、Web 產品化 | C |

---

## 三、現況快照（2026-06-22）

| 項目 | 狀態 |
|------|------|
| `work_flow` + 五條 `run.py` flow | 完成 |
| `modules/file_store`、`setup_workspace`、`setup_project_folders`、`format_messages` | 完成 |
| `adapters/telegram`、`adapters/cli` | 完成 |
| 已刪 `services/`、`store/`、`workspace.py`、`legacy_services` | 完成 |
| TG `/projects`、`/switch`、`/newproject`；CLI；`on_text` 讀 active | 經 dispatch / `file_store` |
| CEO Gemini、PM、執行層 | 未做 |

---

## 四、架構 A0 — 分層骨架（已完成）

- [x] `docs/design/src-layout.md`、Cursor rules、`ai-ceo-framework` skill
- [x] `work_flow/registry.py`、Phase A 四 flow（`run.py`）
- [x] `schemas/`、`adapters/dispatch.py`
- [x] 過渡期與 `telegram/` 路徑說明文件化

**驗收**：`.venv/bin/pytest` 全綠；`./run.sh` / `main init-workspace` 與 list/switch/global 行為正常。

---

## 五、架構 A1 — 工具模組與遺留刪除（已完成）

| # | 步驟 | 驗收 |
|---|------|------|
| 1 | `modules/file_store` | `tests/modules/test_file_store*.py` |
| 2 | `modules/setup_workspace` | `init_workspace__work_flow` |
| 3 | `modules/setup_project_folders` | 建專案 API 在 `file_store.core` |
| 4 | flow 僅用 `modules.*.core` | 無 `legacy_services` |
| 5 | `adapters/telegram/` | `router` 已切換 |
| 6 | 刪除舊層；`ceo_cli` → `adapters/cli` | 無 `store/`、`services/` |

- [x] 步驟 1–6

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
- [ ] 步驟 3–5

---

## 七、產品 P-A2 — PM 單專案建局（Harness §2.2 第 2 項）

| # | 步驟 | 架構產物 | 驗收 |
|---|------|----------|------|
| 1 | PM mode 與 `active_project_id` 綁定 | Command 帶 `project_id` / user mode | TG 路由正確 |
| 2 | PM Session per 專案 | `file_store` + `ai_core` | `sessions/pm_<id>.json` |
| 3 | 寫入 **`workers.yaml`**、建立 **`workers/<id>/`** | `setup_project_folders` + flow | kind 校驗 SKILL |
| 4 | **`project_skills.yaml`** | flow + `file_store` | 與 registry 對齊 |
| 5 | 專案狀態摘要（`pm/`、`shared/`） | `show_project_status__work_flow` | 純讀為主 |

- [ ] 步驟 1–5

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
| 1 | **`modules/execution_store`** ← `worker_state` + `execution/*.json` | 單一佇列 | 持久化可恢復 |
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
