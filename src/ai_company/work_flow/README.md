# work_flow — 產品流程（膠水層）

**中文**：依使用者意圖編排步驟；**唯一**可呼叫 `modules/*/core`。

## 統一註冊

- 註冊表：`registry.py` 的 `registry`。
- 啟動註冊：import `work_flow._register`（由 `work_flow` 套件載入時執行，例如 `adapters.dispatch` → `work_flow.dispatch`）。
- 通道請用 `adapters.dispatch.dispatch(command, deps)`，不要直接 import 各 flow 的 `run.py`（除 `_register.py` 登記用）。

## 單一 flow 目錄約定

每個 `<slug>__work_flow/` 僅 **`run.py`** 為公開實作：

| 符號 | 說明 |
|------|------|
| `run(command, deps)` | 執行流程 |
| `register(registry)` | 向 `WorkFlowRegistry` 登記 |

`__init__.py` 保持空白（僅標記 Python 套件）。

## 已註冊流程

| command_type | 目錄 | 說明（中文） |
|--------------|------|----------------|
| `init_workspace` | [`init_workspace__work_flow`](init_workspace__work_flow/README.md) | 建立工作區根與預設索引檔 |
| `list_projects` | [`list_projects__work_flow`](list_projects__work_flow/README.md) | 列出專案與 active |
| `switch_project` | [`switch_project__work_flow`](switch_project__work_flow/README.md) | 切換 active 專案 |
| `create_project` | [`create_project__work_flow`](create_project__work_flow/README.md) | CEO 建專案殼 |
| `add_skill_to_company` | [`add_skill_to_company__work_flow`](add_skill_to_company__work_flow/README.md) | 啟用 global_skills |
| `update_global_config` | [`update_global_config__work_flow`](update_global_config__work_flow/README.md) | 更新 global_config |
| `ceo_chat` | [`ceo_chat__work_flow`](ceo_chat__work_flow/README.md) | CEO 對話（Gemini／Fake） |
| `show_global_config` | [`show_global_config__work_flow`](show_global_config__work_flow/README.md) | 顯示 global_skills / global_config |

新增流程：新增目錄 + `run.py` → 在 `_register.py` 呼叫其 `register(registry)`。

## 共用編排

跨 flow 重複邏輯放 [`_shared/`](_shared/README.md)（非模組）。

規格：[`docs/design/src-layout.md`](../../../docs/design/src-layout.md)
