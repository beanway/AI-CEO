import asyncio
import logging
from enum import Enum

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.config import Settings

logger = logging.getLogger(__name__)


class BotLane(str, Enum):
    MANAGER = "manager"
    EXECUTOR = "executor"


def _user_allowed(settings: Settings, user_id: int | None) -> bool:
    allowed = settings.allowed_user_ids()
    if not allowed:
        return True
    return user_id is not None and user_id in allowed


async def _gate(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    if not _user_allowed(settings, user.id if user else None):
        if update.effective_message:
            await update.effective_message.reply_text("未授權的使用者。")
        return False
    return True


def _lane_reply_prefix(lane: BotLane) -> str:
    if lane == BotLane.MANAGER:
        return "[管理者 Bot · 帳號 A]"
    return "[執行者 Bot · 帳號 B]"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: BotLane = context.application.bot_data["lane"]
    if not await _gate(update, settings):
        return
    prefix = _lane_reply_prefix(lane)
    await update.message.reply_text(
        f"{prefix}\n"
        "AI 虛擬公司已連線。\n"
        "階段一：通訊路由已就緒；管理層 Gemini Session 與 Worker 狀態機將在後續階段接上。"
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: BotLane = context.application.bot_data["lane"]
    if not update.message or not update.message.text:
        return
    if not await _gate(update, settings):
        return
    prefix = _lane_reply_prefix(lane)
    chat_id = update.effective_chat.id if update.effective_chat else "?"
    await update.message.reply_text(
        f"{prefix} 已收到訊息（chat_id={chat_id}）。\n"
        f"內容預覽：{update.message.text[:200]}"
    )


def build_application(token: str, lane: BotLane, settings: Settings) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["settings"] = settings
    app.bot_data["lane"] = lane
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    return app


async def run_dual_bots(settings: Settings) -> None:
    if not settings.telegram_manager_bot_token or not settings.telegram_executor_bot_token:
        raise SystemExit(
            "請在 .env 設定 TELEGRAM_MANAGER_BOT_TOKEN 與 TELEGRAM_EXECUTOR_BOT_TOKEN。\n"
            "可複製 .env.example 後填入 @BotFather 申請的兩組 Token。"
        )

    manager_app = build_application(
        settings.telegram_manager_bot_token, BotLane.MANAGER, settings
    )
    executor_app = build_application(
        settings.telegram_executor_bot_token, BotLane.EXECUTOR, settings
    )

    await manager_app.initialize()
    await executor_app.initialize()
    await manager_app.start()
    await executor_app.start()
    await manager_app.updater.start_polling(drop_pending_updates=True)
    await executor_app.updater.start_polling(drop_pending_updates=True)

    logger.info("雙 Bot polling 已啟動（管理者 + 執行者）")
    try:
        await asyncio.Event().wait()
    finally:
        await manager_app.updater.stop()
        await executor_app.updater.stop()
        await manager_app.stop()
        await executor_app.stop()
        await manager_app.shutdown()
        await executor_app.shutdown()
