# ai_core

**AI 供應商與對話**：模型解析（`resolve_model`）、Fake／Gemini `ChatBackend`（`get_chat_backend`）。

## 對外接口（`core.py`）

- `CEO_SYSTEM_INSTRUCTION`：CEO 對話 system prompt
- `resolve_model(settings, global_config?)`：優先 `global_config.default_model`
- `get_chat_backend(settings)`：有 `GEMINI_API_KEY` 用 Gemini，否則 Fake
- `build_generate_content_config`（`internal/generation_config.py`）：`max_output_tokens`、`thinking_budget=0` 等

## 呼叫者

僅 `work_flow/*__work_flow/run.py`。
