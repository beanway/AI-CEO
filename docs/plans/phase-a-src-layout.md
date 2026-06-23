# Phase A — 原始碼分層重構計畫

**依據**：[`design/src-layout.md`](../design/src-layout.md)、[`design/harness-design.md`](../design/harness-design.md)  
**取代參考**：[`phase-a-management-v1-archived.md`](phase-a-management-v1-archived.md)（僅歷史，勿執行）

---

## 目標

1. 通道（TG / CLI / 日後 Web）只經 **`work_flow.registry`** 執行業務。
2. 工具能力收斂到 **`modules/`**（`file_store`、`setup_workspace` 等）。
3. **DTO** 集中 `schemas/`，改 JSON/YAML 時可追蹤影響面。
4. 各目錄 **README** 供語意目錄索引。

---

## 步驟（建議順序）

### A0 — 骨架與文件（本輪）

- [x] `docs/design/src-layout.md`、本計畫
- [x] `work_flow/registry.py`、`_register.py`、Phase A flows（**公開 `run.py`**）
- [x] 過渡期說明（skill、`python-harness`、adapters/telegram 對照）
- [x] `schemas/commands.py`、`results.py`、`documents.py`
- [x] `adapters/dispatch.py`；TG / CLI 改走 dispatch
- [x] Cursor rules、專案 skill、README 更新

### A1 — 模組遷移（進行中／待辦）

- [ ] `modules/file_store` ← `store/company_store.py`
- [ ] `modules/setup_workspace` ← `workspace.py`、`services/migrate.py`
- [ ] `modules/setup_project_folders` ← `services/project_paths.py`
- [ ] `modules/format_messages` ← `format_projects_message` 等
- [ ] flows 改為只呼叫 `modules.*.core`
- [ ] 遷移 `telegram/` → `adapters/telegram/`
- [ ] 刪除 `services/`、`store/`、根層 `workspace.py`、`ceo_cli.py`（併入 `adapters/cli`）

### A2 — 與 Harness Phase A 產品對齊

- [ ] `create_project__work_flow`（建殼）
- [ ] `add_skill_to_company__work_flow`（CEO global skill）
- [ ] CEO Session / Gemini（`ai_core` + 新 flow）

---

## 驗收（A0）

- `./run.sh` 與 `python -m ai_company.main run` 行為與重構前一致（list/switch/init/global）。
- `python -c "from ai_company.work_flow.registry import registry; print(registry.list_flows())"` 列出已註冊 flow。
- 文件索引 [`docs/README.md`](../README.md) 含 `src-layout.md`。
