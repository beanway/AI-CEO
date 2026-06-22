# 實作路線圖

**依據**：[`design/harness-design.md`](design/harness-design.md)  
**摘要**：[`discussion-outcomes.md`](discussion-outcomes.md)

---

## 現況（程式碼）

| 項目 | 狀態 | 備註 |
|------|------|------|
| 雙 Bot Router 骨架 | 已存在 | 管理者 Bot：`/projects`、`/switch` |
| `company_workspace` 扁平目錄 | 已存在 | **與設計衝突**，待遷移 |
| `_company` 索引（projects / global YAML） | 已實作 | `CompanyStore` + `init-workspace` |
| Harness 設計 | 已文件化 | 待實作 |
| Phase A 實作計畫 | 已歸檔 | 見 `plans/phase-a-management-v1-archived.md`，**待依 Harness 重寫** |

---

## Phase A1 — CEO（全公司）

- [x] `_company/projects.json`、`global_skills.yaml`、`global_config.yaml`
- [x] `/projects`、`/switch`、active 專案
- [ ] CEO Session（Gemini 或階段性 Fake 後端）
- [ ] `/newproject` 建殼（專案目錄 + PM Session 索引，**不含** Worker 編制）

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
- [ ] `ToolPolicy` + `SandboxRunner`
- [ ] 執行者 Bot 進度與失敗 TG（重試 / code review）
- [ ] `scheduler_decisions.jsonl`（無結構化評分）

## Phase B+ — Skill 生態

- [ ] `skills/registry/` + CEO/PM 啟用流程
- [ ] find-skills / create-skill adapter

## Phase C — 閉環

- [ ] QA 回流、至 `PROJECT_DONE`

## 第二期

- [ ] COO `metrics/usage.jsonl`
- [ ] 網頁 API（共用 CompanyService）
- [ ] 結構化 AI 任務評分

---

## 遷移待辦

- [ ] `company_workspace` → `projects/<id>/` 結構
- [ ] 更新 `src/ai_company/workspace.py` 與文件一致
