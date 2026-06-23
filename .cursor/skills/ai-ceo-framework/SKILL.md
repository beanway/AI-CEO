---
name: ai-ceo-framework
description: >-
  Edit AI-CEO Harness Python framework (src/ai_company). Use when changing
  Router, work_flow, modules, adapters, schemas, or docs that must match
  src-layout and harness-design.
---

# AI-CEO 框架開發規範

## 先讀文件

1. 產品／治理：[`docs/design/harness-design.md`](../../../docs/design/harness-design.md)
2. **程式分層（Canonical）**：[`docs/design/src-layout.md`](../../../docs/design/src-layout.md)
3. 重構計畫：[`docs/plans/phase-a-src-layout.md`](../../../docs/plans/phase-a-src-layout.md)

## 分層（必守）

| 層 | 路徑 | 規則 |
|----|------|------|
| 通道 | `adapters/` | 解析 TG/CLI/Web → `schemas.commands`；只呼叫 `adapters.dispatch` |
| 流程 | `work_flow/` | 編排業務；**唯一**可 `import modules.<name>.core` |
| 工具 | `modules/` | 無流程；對外僅 `core.py` + `README.md` |
| 契約 | `schemas/` | Command / Result / Document DTO |

- 新增產品功能：新增 `work_flow/<slug>__work_flow/run.py`（`run` + `register`），並在 `work_flow/_register.py` 登記。

## 過渡期例外（至 P-A1+ 完成）

- `adapters/telegram/manager_handlers.on_text` 可暫用 `file_store.get_active_project`（尚未有 chat flow）。

- **新功能與新指令**仍須 `dispatch` + 新 `*__work_flow/run.py`。

## 工具模組命名（README 第一行寫中文）

| 目錄 | 用途 |
|------|------|
| `file_store` | 讀寫 JSON/YAML 設定檔 |
| `setup_workspace` | 工作區根目錄建立與遷移 |
| `setup_project_folders` | 單專案 `projects/<id>/` 資料夾樹 |
| `format_messages` | Result/DTO → 回覆文字 |
| `ai_core` | AI provider 與模型（Phase B+） |
| `execution_store` | 執行狀態持久化 |
| `sandbox_runner` | 沙盒 subprocess |
| `notify` | 出站通知 |

## DTO

- 改 `company_workspace/_company/` 內 JSON/YAML：**先**改 `schemas/documents.py` 與 owning 模組 README。
- 跨通道只傳 `schemas` 的 Command/Result，不傳未封裝的 store 內部型別。

## Harness 邊界

- 沙盒產物只在 `company_workspace/projects/<project_id>/`。
- Worker 不修改 `src/`；Cursor 只開發框架本身。
- CEO 全公司 vs PM 單專案：體現在**哪條 flow** 被註冊與 dispatch，見 harness-design。

## 檔名

- 目錄與 `.py` 一律**英文**；`README.md` 可中文說明語意。
