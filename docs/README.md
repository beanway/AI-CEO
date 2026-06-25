# 文件索引

本目錄為 **AI 虛擬公司（AI Company Framework）** 唯一文件根。

- **產品／治理（Canonical）**：[`design/harness-design.md`](design/harness-design.md)
- **原始碼分層（Canonical）**：[`design/src-layout.md`](design/src-layout.md)

## 閱讀順序（建議）

1. [`discussion-outcomes.md`](discussion-outcomes.md) — 討論後共識（精簡、中文）
2. [`design/harness-design.md`](design/harness-design.md) — Harness + 動態 Worker
3. [`design/src-layout.md`](design/src-layout.md) — `src/ai_company` 分層、work_flow 註冊、modules 命名
4. [`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md) — Phase A 程式重構計畫
5. [`roadmap.md`](roadmap.md) — 實作階段與檢查清單
6. [`design/execution-layer-v2.md`](design/execution-layer-v2.md) — **執行層 v2**（真實 Worker、先 backend）
7. [`document-audit.md`](document-audit.md) — 文件與程式碼一致性審查

## 目錄結構

| 路徑 | 說明 |
|------|------|
| [`discussion-outcomes.md`](discussion-outcomes.md) | 產品決策與 Harness 對照摘要 |
| [`design/harness-design.md`](design/harness-design.md) | 產品設計規格 |
| [`design/execution-layer-v2.md`](design/execution-layer-v2.md) | 執行層 v2：AI 排程願景、E1 backend |
| [`design/src-layout.md`](design/src-layout.md) | **框架程式目錄與依賴規則** |
| [`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md) | Phase A 分層重構（現行計畫） |
| [`design/framework-design-v1-archived.md`](design/framework-design-v1-archived.md) | 初版設計（已廢止） |
| [`plans/phase-a-management-v1-archived.md`](plans/phase-a-management-v1-archived.md) | 舊 Phase A（已廢止） |
| [`reference/original-spec.txt`](reference/original-spec.txt) | 歷史原文 |
| [`roadmap.md`](roadmap.md) | 路線圖 |
| [`../worker_default/README.md`](../worker_default/README.md) | E1 預設 Worker 模板目錄 |
| [`../worker_default/SKILL_EXECUTION_ENV.md`](../worker_default/SKILL_EXECUTION_ENV.md) | Skill 執行環境（不用 MCP） |
| [`document-audit.md`](document-audit.md) | 衝突與待辦 |

## Cursor 規則與 Skill

| 資源 | 作用 |
|------|------|
| [`.cursor/rules/`](../.cursor/rules/) | Project Rules（`.mdc`） |
| `harness-architecture.mdc` | 每次對話：Harness + src-layout 指標 |
| `python-harness.mdc` | 編輯 `src/**/*.py` 時的分層慣例 |
| [`.cursor/skills/ai-ceo-framework/`](../.cursor/skills/ai-ceo-framework/SKILL.md) | 開發本 repo 時的框架規範 skill |

虛擬公司 **Worker** 的 skill 見 Harness 設計 §5；與上述 Cursor 開發 skill **勿混用**。

## 外部連結

- [Google Doc（來源）](https://docs.google.com/document/d/1tioCDz0Gb1nVmcIfdasC70zE456Z7SVSy9StZKsdKpo/edit)
