# 文件索引

本目錄為 **AI 虛擬公司（AI Company Framework）** 唯一文件根。實作與討論以 **`design/harness-design.md`** 為準。

## 閱讀順序（建議）

1. [`discussion-outcomes.md`](discussion-outcomes.md) — 討論後共識（精簡、中文）
2. [`design/harness-design.md`](design/harness-design.md) — **現行設計規格（Harness + 動態 Worker）**
3. [`roadmap.md`](roadmap.md) — 實作階段與檢查清單
4. [`document-audit.md`](document-audit.md) — 文件與程式碼一致性審查

## 目錄結構

| 路徑 | 說明 |
|------|------|
| [`discussion-outcomes.md`](discussion-outcomes.md) | 產品決策與 Harness 對照摘要 |
| [`design/harness-design.md`](design/harness-design.md) | **Canonical 設計規格** |
| [`design/framework-design-v1-archived.md`](design/framework-design-v1-archived.md) | 初版設計（固定五目錄，已廢止） |
| [`reference/original-spec.txt`](reference/original-spec.txt) | 最早 Google Doc／Word 匯出原文（歷史參考） |
| [`plans/phase-a-management-v1-archived.md`](plans/phase-a-management-v1-archived.md) | 依初版 spec 的 Phase A 計畫（已廢止，待重寫） |
| [`roadmap.md`](roadmap.md) | 路線圖（對齊 Harness 設計） |
| [`document-audit.md`](document-audit.md) | 衝突與待辦 |

## 外部連結

- [Google Doc（來源）](https://docs.google.com/document/d/1tioCDz0Gb1nVmcIfdasC70zE456Z7SVSy9StZKsdKpo/edit)

## Cursor 專案規則

本 repo 使用 **Project Rules**（Cursor 現行做法），目錄： [`.cursor/rules/`](../.cursor/rules/)

| 檔案 | 作用 |
|------|------|
| `harness-architecture.mdc` | `alwaysApply: true` — 每次對話都帶入 Harness／CEO/PM 邊界 |
| `python-harness.mdc` | `globs: src/**/*.py` — 編輯 Python 時額外套用路徑與分層慣例 |

### 用法（Cursor）

1. **自動套用**：`alwaysApply: true` 的規則在專案內 Chat / Agent 會自動注入上下文（無需 @ 檔名）。
2. **依檔案套用**：開啟或編輯符合 `globs` 的檔案時，對應規則會加入（例如編輯 `src/**/*.py`）。
3. **手動引用**：在輸入框用 **@Rules** 或規則選擇器可查看／附加專案規則（依 Cursor 版本 UI 可能為 *Rules*、*Project Rules*）。
4. **與 `.cursorrules` 的關係**：根目錄 `.cursorrules` 為舊式單檔；本專案已遷至 `.cursor/rules/*.mdc`，內容以 `.mdc` 為準。
5. **與 Worker skill 無關**：此處規則只約束 **開發本 repo 的 Cursor Agent**；虛擬公司 Worker 的 skill 見 Harness 設計 §5。

新增規則：在 `.cursor/rules/` 新增 `.mdc`，YAML frontmatter 需含 `description`，並設 `alwaysApply` 或 `globs`（詳見 Cursor 文件 *Rules* / create-rule 技能）。
