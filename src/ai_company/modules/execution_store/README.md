# execution_store

**執行狀態持久化**：`company_workspace/_company/execution/`、全公司單一 Worker 佇列（Phase B）。

- `execution/<id>.json`：單次 Worker 執行狀態
- `execution/queue.json`：`ExecutionQueueFile` 待派工佇列
