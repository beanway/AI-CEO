"""出站通知（Phase B）：執行者 Telegram Bot 等。"""

from __future__ import annotations

_NOT_IMPLEMENTED = "notify 尚未實作（Phase B）"


async def send_executor_message(chat_id: int, text: str) -> None:
    raise NotImplementedError(_NOT_IMPLEMENTED)
