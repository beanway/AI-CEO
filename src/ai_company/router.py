import asyncio
import logging
from enum import Enum

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from ai_company.adapters.telegram.executor_handlers import (
    cmd_start_executor,
    on_text_executor,
)
from ai_company.adapters.telegram.manager_handlers import register_manager_handlers
from ai_company.config import Settings
from ai_company.modules.file_store import core as file_store
from ai_company.modules.setup_workspace import core as setup_workspace

logger = logging.getLogger(__name__)


class BotLane(str, Enum):
    MANAGER = "manager"
    EXECUTOR = "executor"


def build_manager_application(token: str, settings: Settings) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["settings"] = settings
    app.bot_data["lane"] = BotLane.MANAGER
    register_manager_handlers(app)
    return app


def build_executor_application(token: str, settings: Settings) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["settings"] = settings
    app.bot_data["lane"] = BotLane.EXECUTOR
    app.add_handler(CommandHandler("start", cmd_start_executor))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_executor))
    return app


async def run_dual_bots(settings: Settings) -> None:
    if not settings.telegram_manager_bot_token or not settings.telegram_executor_bot_token:
        raise SystemExit(
            "請在 .env 設定 TELEGRAM_MANAGER_BOT_TOKEN 與 TELEGRAM_EXECUTOR_BOT_TOKEN。\n"
            "可複製 .env.example 後填入 @BotFather 申請的兩組 Token。"
        )

    setup_workspace.ensure_workspace(settings.workspace_root)
    file_store.bootstrap_default_project_if_needed(settings.workspace_root)

    manager_app = build_manager_application(settings.telegram_manager_bot_token, settings)
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
