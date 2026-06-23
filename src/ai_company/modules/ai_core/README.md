# ai_core

**AI 供應商與對話**：Fake／Gemini `ChatBackend`；執行期生成參數由 `configure_generation()` 套用。

## 對外接口（`core.py`）

- `CEO_SYSTEM_INSTRUCTION`
- `configure_generation(AiGenerationSettings)`：建立 chat 前設定（thinking、max_output_tokens 等）
- `current_generation()`：目前套用中的參數
- `get_chat_backend(AppSettings)`：有 resolved API key 用 Gemini，否則 Fake

參數來源：`modules/settings` 從 `global_config.yaml` 解析後，由 `ceo_chat__work_flow` 呼叫 `configure_generation`。

## 呼叫者

僅 `work_flow/*__work_flow/run.py`（與診斷腳本）。
