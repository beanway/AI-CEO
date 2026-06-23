# modules — 可重用工具（無流程）

各子目錄為**工具模組**；**流程**只在 `work_flow/`。  
**僅 `work_flow` 可 import 各模組的 `core.py`**（`adapters` 走 `dispatch`；`adapters/telegram` 可 import `file_store.core` 僅用於過渡期 `on_text` 讀 active，日後改 flow）。

| 目錄 | 中文 | 狀態 |
|------|------|------|
| [`file_store`](file_store/README.md) | 設定檔讀寫 | 已建立 |
| [`setup_workspace`](setup_workspace/README.md) | 工作區根目錄建立 | 已建立 |
| [`setup_project_folders`](setup_project_folders/README.md) | 專案資料夾建立 | 已建立 |
| [`format_messages`](format_messages/README.md) | 回覆排版 | 已建立 |
| `ai_core` | AI 供應商與對話 | Phase A（CEO chat） |
| `execution_store` | 執行狀態持久化 | Phase B |
| `sandbox_runner` | 沙盒指令執行 | Phase B |
| `notify` | 出站通知 | Phase B |

規格：[`docs/design/src-layout.md`](../../../docs/design/src-layout.md)
