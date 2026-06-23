# modules — 可重用工具（無流程）

各子目錄為**工具模組**；**流程**只在 `work_flow/`。  
**僅 `work_flow` 可 import 各模組的 `core.py`**（`adapters` 走 `dispatch`）。

| 目錄 | 中文 | 狀態 |
|------|------|------|
| [`format_messages`](format_messages/README.md) | 回覆排版 | 已建立 |
| `file_store` | 設定檔讀寫 | 待遷移（現：`store/`） |
| `setup_workspace` | 工作區根目錄建立 | 待遷移（現：`workspace.py`） |
| `setup_project_folders` | 專案資料夾建立 | 待遷移（現：`services/project_paths.py`） |
| `ai_core` | AI 供應商與對話 | Phase B+ |
| `execution_store` | 執行狀態持久化 | Phase B |
| `sandbox_runner` | 沙盒指令執行 | Phase B |
| `notify` | 出站通知 | Phase B |

規格：[`docs/design/src-layout.md`](../../../docs/design/src-layout.md)
