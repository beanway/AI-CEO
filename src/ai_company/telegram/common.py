from telegram import Update

from ai_company.config import Settings


def user_allowed(settings: Settings, user_id: int | None) -> bool:
    allowed = settings.allowed_user_ids()
    if not allowed:
        return True
    return user_id is not None and user_id in allowed


async def gate_message(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    if not user_allowed(settings, user.id if user else None):
        if update.effective_message:
            await update.effective_message.reply_text("未授權的使用者。")
        return False
    return True
