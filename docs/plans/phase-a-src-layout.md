# Phase A — 原始碼分層重構計畫

**依據**：[`design/src-layout.md`](../design/src-layout.md)、[`design/harness-design.md`](../design/harness-design.md)  
**取代參考**：[`phase-a-management-v1-archived.md`](phase-a-management-v1-archived.md)（僅歷史，勿執行）  
**執行勾選**：[`roadmap.md`](../roadmap.md)

---

## 目標

1. 通道（TG / CLI / 日後 Web）只經 **`work_flow.registry`** 執行業務。
2. 工具能力收斂到 **`modules/`**（`file_store`、`setup_workspace` 等）。
3. **DTO** 集中 `schemas/`，改 JSON/YAML 時可追蹤影響面。
4. 各目錄 **README** 供語意目錄索引。

---

## 步驟

### A0 — 骨架與文件

- [x] 見 roadmap §四

### A1 — 模組遷移

- [x] `modules/file_store`
- [x] `modules/setup_workspace`
- [x] `modules/setup_project_folders`
- [x] flows → `modules.*.core`；刪 `legacy_services`
- [x] `adapters/telegram/`
- [x] 刪 `services/`、`store/`、`workspace.py`；CLI `adapters/cli`

### A2 — 與 Harness Phase A 產品對齊

- [x] `create_project__work_flow`（建殼）
- [x] `add_skill_to_company__work_flow`（CEO global skill）
- [x] `update_global_config__work_flow`
- [x] CEO Session / Gemini（`ai_core` + `ceo_chat__work_flow`）

---

## 驗收

- `.venv/bin/pytest -q` 全綠
- `registry.list_flows()` 含 Phase A 四 flow
