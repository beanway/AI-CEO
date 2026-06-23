from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.schemas.documents import SessionRecord, utc_now
from ai_company.modules.ai_core import core as ai_core
from ai_company.modules.file_store import core as file_store
from ai_company.modules.settings import core as app_settings
from ai_company.schemas.commands import BaseCommand, CeoChatCommand, CommandType
from ai_company.schemas.results import CeoChatResult
from ai_company.work_flow.registry import WorkFlowRegistry


def _ensure_ceo_handle(
    deps: AppDeps,
    backend: object,
    *,
    model: str,
) -> SessionRecord:
    record = file_store.load_ceo_session(deps.workspace_root)
    if record is None:
        record = SessionRecord(gemini_chat_name="", project_id=None)
    name = record.gemini_chat_name
    if not name or record.stale or not backend.has_chat(name):
        name = backend.create_chat(
            system_instruction=ai_core.CEO_SYSTEM_INSTRUCTION,
            model=model,
        )
        record = SessionRecord(gemini_chat_name=name, project_id=None, stale=False)
        file_store.save_ceo_session(deps.workspace_root, record)
    return record


def _send_with_recovery(
    deps: AppDeps,
    backend: object,
    record: SessionRecord,
    text: str,
    *,
    model: str,
) -> tuple[str, SessionRecord]:
    try:
        reply = backend.send_message(record.gemini_chat_name, text, model=model)
    except Exception:
        name = backend.create_chat(
            system_instruction=ai_core.CEO_SYSTEM_INSTRUCTION,
            model=model,
        )
        record = SessionRecord(gemini_chat_name=name, project_id=None, stale=False)
        file_store.save_ceo_session(deps.workspace_root, record)
        reply = backend.send_message(name, text, model=model)
    record = record.model_copy(update={"updated_at": utc_now(), "stale": False})
    file_store.save_ceo_session(deps.workspace_root, record)
    return reply, record


def run(command: BaseCommand, deps: AppDeps) -> CeoChatResult:
    if not isinstance(command, CeoChatCommand):
        return CeoChatResult(success=False, message="指令類型錯誤", error_code="bad_command")
    text = command.text.strip()
    if not text:
        return CeoChatResult(
            success=False,
            message="訊息不可為空白",
            error_code="invalid_text",
        )
    file_store.ensure_company_dirs(deps.workspace_root)
    global_config = file_store.load_global_config(deps.workspace_root)
    ai_core.configure_generation(app_settings.resolve_ai_generation(global_config))
    model = app_settings.resolve_model(global_config)
    backend = ai_core.get_chat_backend(deps.settings)
    try:
        record = _ensure_ceo_handle(deps, backend, model=model)
        reply, _ = _send_with_recovery(deps, backend, record, text, model=model)
    except Exception as exc:
        return CeoChatResult(
            success=False,
            message=f"CEO 對話失敗：{exc}",
            error_code="ceo_chat_failed",
        )
    return CeoChatResult(success=True, message=reply, reply=reply)


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.CEO_CHAT,
        flow_id="ceo_chat__work_flow",
        description_zh="CEO Session 對話（Gemini 或 Fake）",
        runner=run,
    )
