from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.adapters.dispatch import dispatch
from ai_company.adapters.telegram.gate import gate_message
from ai_company.app_deps import AppDeps
from ai_company.config import Settings
from ai_company.modules.file_store import core as file_store
from ai_company.schemas.commands import (
    AddSkillToCompanyCommand,
    AddSkillToProjectCommand,
    Channel,
    CeoChatCommand,
    CreateProjectCommand,
    ListProjectsCommand,
    PmChatCommand,
    SetUserModeCommand,
    SetupWorkersCommand,
    ShowProjectStatusCommand,
    SwitchProjectCommand,
)
from ai_company.schemas.documents import UserMode


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    await update.message.reply_text(
        "[管理者 Bot · 帳號 A]\n"
        "AI 虛擬公司已連線。\n"
        "指令：/projects、/switch <id>、/newproject <名稱>、/addskill <id>；"
        "/mode ceo|pm、/status、/setupworkers five|three、/addprojectskill <id>；"
        "其餘文字依模式由 CEO 或 PM（Gemini）回覆。"
    )


async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    result = dispatch(ListProjectsCommand(channel=Channel.TELEGRAM), deps)
    await update.message.reply_text(result.message)


async def cmd_newproject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/newproject <專案名稱>")
        return
    name = " ".join(context.args).strip()
    deps = AppDeps(settings=settings)
    result = dispatch(
        CreateProjectCommand(channel=Channel.TELEGRAM, name=name),
        deps,
    )
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


async def cmd_addskill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/addskill <registry skill id>")
        return
    skill_id = context.args[0].strip()
    deps = AppDeps(settings=settings)
    result = dispatch(
        AddSkillToCompanyCommand(channel=Channel.TELEGRAM, skill_id=skill_id),
        deps,
    )
    await update.message.reply_text(result.message)


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args or context.args[0].lower() not in ("ceo", "pm"):
        await update.message.reply_text("用法：/mode ceo 或 /mode pm")
        return
    user = update.effective_user
    if user is None:
        return
    mode = UserMode.PM if context.args[0].lower() == "pm" else UserMode.CEO
    deps = AppDeps(settings=settings)
    result = dispatch(
        SetUserModeCommand(channel=Channel.TELEGRAM, telegram_user_id=user.id, mode=mode),
        deps,
    )
    await update.message.reply_text(result.message)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    result = dispatch(ShowProjectStatusCommand(channel=Channel.TELEGRAM), deps)
    await update.message.reply_text(result.message)


async def cmd_setupworkers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args or context.args[0] not in ("five", "three"):
        await update.message.reply_text("用法：/setupworkers five 或 /setupworkers three")
        return
    deps = AppDeps(settings=settings)
    result = dispatch(
        SetupWorkersCommand(channel=Channel.TELEGRAM, template=context.args[0]),
        deps,
    )
    await update.message.reply_text(result.message)


async def cmd_addprojectskill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/addprojectskill <registry skill id>")
        return
    skill_id = context.args[0].strip()
    deps = AppDeps(settings=settings)
    result = dispatch(
        AddSkillToProjectCommand(channel=Channel.TELEGRAM, skill_id=skill_id),
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
    user = update.effective_user
    user_id = user.id if user else 0
    mode = file_store.get_user_mode(deps.workspace_root, user_id)
    if mode == UserMode.PM:
        result = dispatch(
            PmChatCommand(channel=Channel.TELEGRAM, text=update.message.text),
            deps,
        )
    else:
        result = dispatch(
            CeoChatCommand(channel=Channel.TELEGRAM, text=update.message.text),
            deps,
        )
    if not result.success:
        await update.message.reply_text(result.message)
        return
    reply = getattr(result, "reply", None) or result.message
    await update.message.reply_text(reply)


def register_manager_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("newproject", cmd_newproject))
    app.add_handler(CommandHandler("addskill", cmd_addskill))
    app.add_handler(CommandHandler("switch", cmd_switch))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("setupworkers", cmd_setupworkers))
    app.add_handler(CommandHandler("addprojectskill", cmd_addprojectskill))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
