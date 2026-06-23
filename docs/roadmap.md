# 實作路線圖

**依據**：[`design/harness-design.md`](design/harness-design.md)、[`design/src-layout.md`](design/src-layout.md)  
**摘要**：[`discussion-outcomes.md`](discussion-outcomes.md)  
**程式重構**：[`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md)

---

## 現況（程式碼）

| 項目 | 狀態 | 備註 |
|------|------|------|
| 雙 Bot Router 骨架 | 已存在 | 管理者：`/projects`、`/switch` 經 `dispatch` |
| `work_flow` 統一註冊 | 已建立 | Phase A 四條 flow |
| `schemas` + `adapters.dispatch` | 已建立 | TG / CLI / main init-workspace |
| `modules/format_messages` | 已建立 | 其餘工具模組待遷移 |
| `company_workspace` 扁平目錄 | 可能仍存在 | 啟動時 `setup_workspace`（遷移中：`workspace.py`） |
| `_company` 索引 | 已實作 | 目標：`modules/file_store` |
| 舊 `services/`、`store/` | 過渡期 | 見 phase-a-src-layout A1 |

---

## Phase A0 — 分層骨架

- [x] `docs/design/src-layout.md`
- [x] `work_flow/registry` + Phase A flows
- [x] Cursor rules + `ai-ceo-framework` skill

## Phase A1 — CEO（全公司）

- [x] `_company/projects.json`、`global_skills.yaml`、`global_config.yaml`
- [x] `/projects`、`/switch`、active 專案（經 work_flow）
- [ ] 模組遷移：`file_store`、`setup_workspace`、`setup_project_folders`
- [ ] CEO Session（Gemini 或階段性 Fake 後端）
- [ ] `/newproject` → `create_project__work_flow`

## Phase A2 — PM（單專案建局）

- [ ] PM Session  per `project_id`
- [ ] `workers.yaml` + `workers/<id>/` 動態建立
- [ ] `project_skills.yaml`
- [ ] 專案狀態查詢（`pm/`、`shared/` 摘要）

## Phase A3 — PM 維修與 Git

- [ ] Git 限專案目錄；高風險操作 TG Inline 核准
- [ ] 維修流程（與 execution 狀態協同，可先手動）

## Phase B — Harness 執行

- [ ] `task_scheduler` Worker + 單一執行佇列
- [ ] `modules/sandbox_runner` + ToolPolicy
- [ ] `modules/notify`、執行者 Bot 進度與失敗 TG
- [ ] `scheduler_decisions.jsonl`（無結構化評分）

## Phase B+ — Skill 生態

- [ ] `skills/registry/` + `add_skill_to_company__work_flow`
- [ ] find-skills / create-skill adapter

## Phase C — 閉環

- [ ] QA 回流、至 `PROJECT_DONE`

## 第二期

- [ ] COO `metrics/usage.jsonl`
- [ ] 網頁 API（共用 `dispatch` + Command）
- [ ] 結構化 AI 任務評分

---

## 遷移待辦

- [ ] 刪除過渡 `services/`、`store/` 根層 `workspace.py`（完成 A1 模組遷移後）
- [ ] `worker_state.py` → `modules/execution_store` + flow（Phase B）
