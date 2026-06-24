# notify

**出站通知**：執行者 Bot（帳號 B）進度與失敗訊息；排程邏輯在專案 `task_scheduler` Worker。

`send_executor_message` 經 `set_notify_sink` 可注入；未注入時不發送。
