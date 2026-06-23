# settings

**集中設定**：讀取 `.env`（`AppSettings`）與解析 `global_config.yaml` 欄位（`resolve_ai_generation`、`resolve_model`）。

## 對外接口（`core.py`）

- `load_settings()` → `AppSettings`
- `resolved_gemini_api_key()`：官網順序 **GOOGLE_API_KEY** → **GEMINI_API_KEY**
- `resolved_gemini_api_key_source()`：`'google' | 'gemini' | None`（不含 secret）
- `resolve_model(global_config?)`、`resolve_ai_generation(global_config?)`

## 呼叫者

`config.py`（相容別名）、`work_flow`（對話前套用）、`adapters`、`main`。

AI 執行期套用：`work_flow` 呼叫 `ai_core.configure_generation(...)`。
