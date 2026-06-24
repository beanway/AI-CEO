# web

**二期 Web 通道**：`POST /api/v1/dispatch` 傳入與 `schemas.commands` 相同的 JSON；經 `adapters.dispatch`。

- `GET /health`：存活檢查
- 若 `.env` 設定 `WEB_API_KEY`，須帶 `Authorization: Bearer <key>`

啟動：`python -m ai_company.adapters.web --port 8765`
