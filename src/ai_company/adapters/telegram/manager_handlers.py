from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from ai_company.adapters.dispatch import dispatch
from ai_company.adapters.telegram.approval_replies import reply_with_optional_approval
from ai_company.adapters.telegram.approval_ui import parse_approval_callback
from ai_company.adapters.telegram.gate import gate_message
from ai_company.adapters.telegram.help_text import MANAGER_HELP_TEXT
from ai_company.app_deps import AppDeps
from ai_company.config import Settings
from ai_company.schemas.commands import (
    AddSkillToCompanyCommand,
    AddSkillToProjectCommand,
    Channel,
    CreateProjectCommand,
    ListProjectsCommand,
    PmRepairCommand,
    ProjectGitCommand,
    RemoveSkillFromCompanyCommand,
    ResolveApprovalCommand,
    RouteManagerChatCommand,
    SetUserModeCommand,
    SetupWorkersCommand,
    ShowGlobalConfigCommand,
    ShowProjectStatusCommand,
    SwitchProjectCommand,
    UpdateGlobalConfigCommand,
)
from ai_company.schemas.documents import NotificationPolicy, UserMode


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    await update.message.reply_text(
        "[管理者 Bot · 帳號 A]\n"
        "AI 虛擬公司已連線。\n"
        "輸入 /help 查看完整指令列表；其餘文字依 /mode 由 CEO 或 PM（Gemini）回覆。"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    await update.message.reply_text(MANAGER_HELP_TEXT)


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


async def cmd_global(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    result = dispatch(ShowGlobalConfigCommand(channel=Channel.TELEGRAM), deps)
    await update.message.reply_text(result.message)


async def cmd_removeskill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/removeskill <registry skill id>")
        return
    skill_id = context.args[0].strip()
    deps = AppDeps(settings=settings)
    result = dispatch(
        RemoveSkillFromCompanyCommand(channel=Channel.TELEGRAM, skill_id=skill_id),
        deps,
    )
    await update.message.reply_text(result.message)


async def cmd_updateglobal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "用法：/updateglobal <欄位> <值>\n"
            "欄位：model、notification（all|failures_only|off）、"
            "dispatch_min_score（0–100）、temperature（浮點數）"
        )
        return
    field = context.args[0].strip().lower()
    value = " ".join(context.args[1:]).strip()
    kwargs: dict = {"channel": Channel.TELEGRAM}
    try:
        if field in ("model", "default_model"):
            kwargs["default_model"] = value
        elif field in ("notification", "notification_policy"):
            kwargs["notification_policy"] = NotificationPolicy(value.lower())
        elif field in ("dispatch_min_score", "dispatch-min-score", "min_score"):
            kwargs["dispatch_min_score"] = int(value)
        elif field == "temperature":
            kwargs["temperature"] = float(value)
        else:
            await update.message.reply_text(f"不支援的欄位：{field}")
            return
        command = UpdateGlobalConfigCommand(**kwargs)
    except (ValueError, TypeError) as exc:
        await update.message.reply_text(f"參數錯誤：{exc}")
        return
    deps = AppDeps(settings=settings)
    result = dispatch(command, deps)
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
    user = update.effective_user
    deps = AppDeps(settings=settings)
    result = dispatch(
        AddSkillToProjectCommand(
            channel=Channel.TELEGRAM,
            skill_id=skill_id,
            telegram_user_id=user.id if user else None,
        ),
        deps,
    )
    await reply_with_optional_approval(update, result)


async def cmd_repair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    interrupt = bool(context.args and context.args[0].lower() == "interrupt")
    deps = AppDeps(settings=settings)
    result = dispatch(
        PmRepairCommand(channel=Channel.TELEGRAM, interrupt=interrupt),
        deps,
    )
    await update.message.reply_text(result.message)


async def cmd_git(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not await gate_message(update, settings):
        return
    if not context.args:
        await update.message.reply_text("用法：/git <git 子命令與參數…>，例：/git status")
        return
    user = update.effective_user
    deps = AppDeps(settings=settings)
    result = dispatch(
        ProjectGitCommand(
            channel=Channel.TELEGRAM,
            git_argv=list(context.args),
            telegram_user_id=user.id if user else None,
        ),
        deps,
    )
    await reply_with_optional_approval(update, result)


async def on_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    query = update.callback_query
    if query is None:
        return
    if not await gate_message(update, settings):
        return
    parsed = parse_approval_callback(query.data or "")
    if parsed is None:
        await query.answer("無效的核准按鈕")
        return
    approved, approval_id = parsed
    user = update.effective_user
    deps = AppDeps(settings=settings)
    result = dispatch(
        ResolveApprovalCommand(
            channel=Channel.TELEGRAM,
            approval_id=approval_id,
            approved=approved,
            telegram_user_id=user.id if user else None,
        ),
        deps,
    )
    await query.answer()
    await query.edit_message_text(result.message)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.application.bot_data["settings"]
    if not update.message or not update.message.text:
        return
    if not await gate_message(update, settings):
        return
    deps = AppDeps(settings=settings)
    user = update.effective_user
    user_id = user.id if user else 0
    result = dispatch(
        RouteManagerChatCommand(
            channel=Channel.TELEGRAM,
            text=update.message.text,
            telegram_user_id=user_id,
        ),
        deps,
    )
    if not result.success:
        await update.message.reply_text(result.message)
        return
    reply = getattr(result, "reply", None) or result.message
    await update.message.reply_text(reply)


def register_manager_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("newproject", cmd_newproject))
    app.add_handler(CommandHandler("addskill", cmd_addskill))
    app.add_handler(CommandHandler("removeskill", cmd_removeskill))
    app.add_handler(CommandHandler("global", cmd_global))
    app.add_handler(CommandHandler("updateglobal", cmd_updateglobal))
    app.add_handler(CommandHandler("switch", cmd_switch))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("repair", cmd_repair))
    app.add_handler(CommandHandler("setupworkers", cmd_setupworkers))
    app.add_handler(CommandHandler("addprojectskill", cmd_addprojectskill))
    app.add_handler(CommandHandler("git", cmd_git))
    app.add_handler(CallbackQueryHandler(on_approval_callback, pattern=r"^approval:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
