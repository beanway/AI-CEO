from telegram import Update
from telegram.ext import ContextTypes

from ai_company.adapters.telegram.gate import gate_message
from ai_company.adapters.telegram.help_text import EXECUTOR_HELP_TEXT
from ai_company.config import Settings


def lane_reply_prefix(lane: str) -> str:
    if lane == "manager":
        return "[管理者 Bot · 帳號 A]"
    return "[執行者 Bot · 帳號 B]"


async def cmd_start_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: str = context.application.bot_data["lane"]
    if not await gate_message(update, settings):
        return
    prefix = lane_reply_prefix(lane)
    await update.message.reply_text(
        f"{prefix}\n"
        "AI 虛擬公司已連線。\n"
        "輸入 /help 查看說明；本 Bot 用於任務進度通知。"
    )


async def cmd_help_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    await update.message.reply_text(EXECUTOR_HELP_TEXT)


async def on_text_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: str = context.application.bot_data["lane"]
    if not update.message or not update.message.text:
        return
    if not await gate_message(update, settings):
        return
    prefix = lane_reply_prefix(lane)
    chat_id = update.effective_chat.id if update.effective_chat else "?"
    await update.message.reply_text(
        f"{prefix} 已收到訊息（chat_id={chat_id}）。\n"
        f"內容預覽：{update.message.text[:200]}"
    )
