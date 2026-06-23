# adapters/telegram — Telegram 通道（目標目錄）

**Phase A0**：管理者／執行者 Bot 程式仍在 **[`../../telegram/`](../../telegram/)**（`manager_handlers.py`、`common.py`），與本目錄語意相同；遷移見 [`docs/plans/phase-a-src-layout.md`](../../../docs/plans/phase-a-src-layout.md)。

職責：解析 `Update` → `schemas.commands` → `adapters.dispatch`；回覆由 `result.message` 送出（或日後 `format_messages` 結構）。
