# 跨邊界資料契約（Command / Result / Document DTO）

- **`commands.py`**：各通道送入 `work_flow.registry` 的指令（含 `command_type`）。
- **`results.py`**：flow 回傳給 adapter 的結果（再由 `format_messages` 或 adapter 送出）。
- **`documents.py`**：對齊 `company_workspace/_company/` 內 JSON/YAML 欄位；改檔案格式時先改此處並更新 [`document-audit`](../../../docs/document-audit.md) 與 `modules/file_store/README.md`。

**規則**：跨模組、跨通道不傳遞未在 `schemas` 定義的持久化物件；模組內部可暫用 `models/`（遷移中）。
