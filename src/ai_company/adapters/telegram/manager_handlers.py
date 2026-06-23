from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.adapters.dispatch import dispatch
from ai_company.adapters.telegram.gate import gate_message
from ai_company.app_deps import AppDeps
from ai_company.config import Settings
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import (
    Channel,
    ListProjectsCommand,
    SwitchProjectCommand,
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    await update.message.reply_text(
        "[管理者 Bot · 帳號 A]\n"
        "AI 虛擬公司已連線。\n"
        "指令：/projects 列出專案、/switch <id> 切換 active 專案。"
    )


async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    result = dispatch(ListProjectsCommand(channel=Channel.TELEGRAM), deps)
    await update.message.reply_text(result.message)


async def cmd_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/switch <專案 id>\n可先 /projects 查看 id。")
        return
    project_id = context.args[0].strip()
    deps = AppDeps(settings=settings)
    result = dispatch(
        SwitchProjectCommand(channel=Channel.TELEGRAM, project_id=project_id),
        deps,
    )
    await update.message.reply_text(result.message)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not update.message or not update.message.text:
        return
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    active = file_store.get_active_project(deps.workspace_root)
    active_line = (
        f"active={active.id}（{active.name}）" if active else "active=（無）"
    )
    await update.message.reply_text(
        f"[管理者] 已收到訊息。{active_line}\n"
        "（CEO Session 將於後續階段接上 Gemini。）"
    )


def register_manager_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("switch", cmd_switch))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
