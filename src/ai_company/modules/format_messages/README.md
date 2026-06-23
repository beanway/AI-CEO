# format_messages

**回覆排版**：把 flow 結果或 Document 摘要轉成 Telegram / CLI 可送出的文字（日後可擴充 TG dict）。

## 對外接口（`core.py`）

| 函式 | 說明 |
|------|------|
| `format_projects_message(pf)` | `ProjectsFile` → 多行文字 |

## 依賴

- 可讀 `schemas.documents` 型別；不讀寫磁碟、不發送訊息。

## 呼叫者

- 僅 `work_flow/*__work_flow/`（過渡期 flow 可直接 import `core`）。
