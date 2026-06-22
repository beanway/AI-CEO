# 討論後共識文檔

**日期**：2026-06-22  
**狀態**：與 [`design/harness-design.md`](design/harness-design.md) 同步  
**說明**：本檔為可讀摘要；細節與驗收條件以 Harness 設計規格為準。

---

## 1. 我們在打造什麼

一套跑在本機的 **AI Harness（駕馭層）**：Python Router + Gemini + 雙 Telegram Bot，模擬「軟體公司」。**你用 Cursor 開發這套系統**；執行層 Worker 只在沙盒內用 Gemini 與工具產出，**不遙控 Cursor IDE Agent**。

對齊 **Harness Engineering** 五重點：防護邊界、環境裝配、工具治理、安全防護、反饋與迭代（見設計規格 §1）。

---

## 2. CEO 與 PM 的邊界

| | CEO | PM |
|---|-----|-----|
| **範圍** | **所有專案**（全公司） | **單一專案**（active `project_id`） |
| **典型動作** | 切換 active 專案、列表；安裝 **全專案共用** skill；`global_config` | 建立 Worker **編制**；專案級 skill；查狀態、維修、Git；**新增 Worker** |
| **建專案** | **建殼**：id、目錄、`projects.json`、PM Session | **建局**：`workers.yaml`、各 `workers/<id>/`、專案 skill |

---

## 3. 工作區：不再使用「全公司一套固定五目錄」

- 正確模型：`company_workspace/projects/<id>/`，每專案有自己的 `shared/`、`pm/`、**動態** `workers/`。
- **範例**
  - 專案 **a**：backend、frontend、planner、**任務分配者**（scheduler）、qa（5 個 Worker）
  - 專案 **b**：backend、planner、scheduler（3 個 Worker，無前端與測試）
- 現有 repo 根下扁平 `company_workspace/shared` 等為 **過渡／錯誤模型**，實作時遷移至 `projects/default/` 或重建。

---

## 4. Worker 與任務分配者

- **Worker 模板（決策 B）**：內建 `kind` 枚舉（`planner`、`backend`、`frontend`、`qa`、`task_scheduler`）+ PM 可新增 **自訂 kind**，並在 `workers/<id>/SKILL.md` 定義能力與允許工具。
- **Skill 來源**：Git、`find-skills`（`npx skills`）、`/create-skill`；CEO 裝 **registry 全公司級**，PM **啟用專案／角色級**（見設計規格 §5.4 疊加順序）。
- **任務分配者**（`task_scheduler`）：專案內 Worker；具 Git、排程、裝工具/skill；失敗時 **TG 詢問** 使用者：**重試** 或 **code review 找問題**。
- **執行者 Bot（帳號 B）**：通知通道；排程邏輯在專案 scheduler Worker，不與管理者 Bot 混用。

---

## 5. 任務評分（決策 B）

- **第一版**：不做結構化「AI 任務評分」作為派工門檻；先 **排程 + TG 人工決策**。
- 可寫 `pm/scheduler_decisions.jsonl` 供日後評分與 COO 分析。
- 結構化評分、COO Token 報表、網頁 UI：**後續階段**。

---

## 6. 實作優先序（產品）

1. CEO：切換專案 + 全公司 global skill／設定  
2. PM：編制、專案 skill、狀態、維修、Git（TG 核准）  
3. 任務分配者 + 狀態機（PM 建局之後）  
4. Skill 生態整合  
5. 端到端 QA 閉環  
6. COO／網頁  

---

## 7. 與原始規格書的關係

[`reference/original-spec.txt`](reference/original-spec.txt) 保留最早敘事（雙 Bot、狀態機、沙盒、PM Git 核准等）。討論後 **增補**：Harness 視角、CEO/PM 全公司 vs 單專案、**動態 Worker 編制**、任務分配者能力、評分策略 B。若與原文衝突，以 **`harness-design.md`** 為準。

---

## 8. 決策一覽

| 主題 | 結論 |
|------|------|
| 建專案 | C：CEO 建殼，PM 建局 |
| Worker 模板 | B：枚舉 + 自訂 kind + `SKILL.md` |
| MVP 介面 | 僅 Telegram |
| COO | 第二期 |
| 任務評分 | B：後加，先 log + 人選 |
| Cursor | 只開發框架，Worker 不遙控 IDE |

---

## 9. 為何文件提到 Cursor？

| 問題 | 說明 |
|------|------|
| **是不是怕改錯檔案？** | 部分相關，但**主要不是**一句「別亂改」而已。 |
| **真正要分的兩層** | **(1) 你用 Cursor 開發 Harness 程式**（`src/`、`docs/`）；(2) **虛擬公司 Worker 只在 `company_workspace/projects/<id>/` 沙盒執行**。 |
| **Worker 不遙控 Cursor** | 執行層不得當成第二個 IDE Agent 去改框架原始碼、其他 repo 或任意本機路徑。 |
| **防改錯檔靠什麼** | 沙盒 **cwd**、**ToolPolicy**（依 Worker `kind`）、CEO/PM 權限分層；不是只靠文件提 Cursor。 |
| **Skill 不要混用** | Cursor / `find-skills` 用於**開發框架**；Worker 用 `skills/registry/` + 專案／角色 YAML。 |

**本 repo 的 Cursor 規則**：見 [`.cursor/rules/`](../.cursor/rules/)（`.mdc`）；舊版根目錄 `.cursorrules` 僅指向該目錄。用法摘要見 [`docs/README.md`](README.md#cursor-專案規則)。
