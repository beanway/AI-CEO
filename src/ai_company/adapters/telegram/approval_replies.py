async def reply_with_optional_approval(update, result) -> None:
    approval_id = getattr(result, "approval_id", None)
    if getattr(result, "error_code", None) == "approval_required" and approval_id:
        from ai_company.adapters.telegram.approval_ui import approval_keyboard

        await update.message.reply_text(result.message, reply_markup=approval_keyboard(approval_id))
        return
    await update.message.reply_text(result.message)
