"""出站通知（Phase B）：執行者 Telegram Bot 等。"""

from __future__ import annotations

from collections.abc import Callable

from ai_company.schemas.documents import NotificationPolicy

NotifySink = Callable[[int, str], None]

_sink: NotifySink | None = None


def set_notify_sink(sink: NotifySink | None) -> None:
    """測試或 adapter 注入；None 表示僅略過（未設定 chat_id 時）。"""
    global _sink
    _sink = sink


def should_notify(policy: NotificationPolicy, *, failed: bool) -> bool:
    if policy == NotificationPolicy.OFF:
        return False
    if policy == NotificationPolicy.FAILURES_ONLY:
        return failed
    return True


def send_executor_message(chat_id: int, text: str) -> None:
    if _sink is not None:
        _sink(chat_id, text)
