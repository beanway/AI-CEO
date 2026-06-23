"""Telegram Inline 核准按鈕。"""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def approval_keyboard(approval_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("核准", callback_data=f"approval:yes:{approval_id}"),
                InlineKeyboardButton("拒絕", callback_data=f"approval:no:{approval_id}"),
            ]
        ]
    )


def parse_approval_callback(data: str) -> tuple[bool, str] | None:
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "approval":
        return None
    approved = parts[1] == "yes"
    if parts[1] not in ("yes", "no"):
        return None
    return approved, parts[2]
