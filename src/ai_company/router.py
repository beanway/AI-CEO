import asyncio
import logging
from enum import Enum

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.config import Settings
from ai_company.services.company_service import CompanyService
from ai_company.telegram.common import gate_message
from ai_company.telegram.manager_handlers import register_manager_handlers

logger = logging.getLogger(__name__)


class BotLane(str, Enum):
    MANAGER = "manager"
    EXECUTOR = "executor"


def _lane_reply_prefix(lane: BotLane) -> str:
    if lane == BotLane.MANAGER:
        return "[管理者 Bot · 帳號 A]"
    return "[執行者 Bot · 帳號 B]"


async def cmd_start_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: BotLane = context.application.bot_data["lane"]
    if not await gate_message(update, settings):
        return
    prefix = _lane_reply_prefix(lane)
    await update.message.reply_text(
        f"{prefix}\n"
        "AI 虛擬公司已連線。\n"
        "執行者 Bot 用於任務進度通知（Phase B 接上排程後啟用）。"
    )


async def on_text_executor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    lane: BotLane = context.application.bot_data["lane"]
    if not update.message or not update.message.text:
        return
    if not await gate_message(update, settings):
        return
    prefix = _lane_reply_prefix(lane)
    chat_id = update.effective_chat.id if update.effective_chat else "?"
    await update.message.reply_text(
        f"{prefix} 已收到訊息（chat_id={chat_id}）。\n"
        f"內容預覽：{update.message.text[:200]}"
    )


def build_manager_application(token: str, settings: Settings, company: CompanyService) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["settings"] = settings
    app.bot_data["lane"] = BotLane.MANAGER
    register_manager_handlers(app, company)
    return app


def build_executor_application(token: str, settings: Settings) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["settings"] = settings
    app.bot_data["lane"] = BotLane.EXECUTOR
    app.add_handler(CommandHandler("start", cmd_start_executor))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_executor))
    return app


async def run_dual_bots(settings: Settings, company: CompanyService) -> None:
    if not settings.telegram_manager_bot_token or not settings.telegram_executor_bot_token:
        raise SystemExit(
            "請在 .env 設定 TELEGRAM_MANAGER_BOT_TOKEN 與 TELEGRAM_EXECUTOR_BOT_TOKEN。\n"
            "可複製 .env.example 後填入 @BotFather 申請的兩組 Token。"
        )

    manager_app = build_manager_application(
        settings.telegram_manager_bot_token, settings, company
    )
    executor_app = build_executor_application(settings.telegram_executor_bot_token, settings)

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
