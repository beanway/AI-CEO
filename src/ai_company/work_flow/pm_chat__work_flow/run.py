from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.schemas.documents import SessionRecord, utc_now
from ai_company.modules.ai_core import core as ai_core
from ai_company.modules.file_store import core as file_store
from ai_company.modules.settings import core as app_settings
from ai_company.schemas.ai_generation import AiGenerationSettings
from ai_company.schemas.commands import BaseCommand, CommandType, PmChatCommand
from ai_company.schemas.results import PmChatResult
from ai_company.work_flow._shared.pm_project import require_active_project_id
from ai_company.work_flow._shared.record_chat_usage import record_chat_usage
from ai_company.work_flow.registry import WorkFlowRegistry


def _ensure_pm_handle(
    deps: AppDeps,
    backend: object,
    project_id: str,
    *,
    model: str,
    generation: AiGenerationSettings,
) -> SessionRecord:
    record = file_store.load_pm_session(deps.workspace_root, project_id)
    if record is None:
        record = SessionRecord(gemini_chat_name="", project_id=project_id)
    name = record.gemini_chat_name
    if not name or record.stale or not backend.has_chat(name):
        name = backend.create_chat(
            system_instruction=ai_core.PM_SYSTEM_INSTRUCTION,
            model=model,
            generation=generation,
        )
        record = SessionRecord(gemini_chat_name=name, project_id=project_id, stale=False)
        file_store.save_pm_session(deps.workspace_root, project_id, record)
    return record


def _send_with_recovery(
    deps: AppDeps,
    backend: object,
    project_id: str,
    record: SessionRecord,
    text: str,
    *,
    model: str,
    generation: AiGenerationSettings,
) -> tuple[str, SessionRecord]:
    try:
        reply = backend.send_message(record.gemini_chat_name, text, model=model)
    except Exception:
        name = backend.create_chat(
            system_instruction=ai_core.PM_SYSTEM_INSTRUCTION,
            model=model,
            generation=generation,
        )
        record = SessionRecord(gemini_chat_name=name, project_id=project_id, stale=False)
        file_store.save_pm_session(deps.workspace_root, project_id, record)
        reply = backend.send_message(name, text, model=model)
    record = record.model_copy(update={"updated_at": utc_now(), "stale": False})
    file_store.save_pm_session(deps.workspace_root, project_id, record)
    return reply, record


def run(command: BaseCommand, deps: AppDeps) -> PmChatResult:
    if not isinstance(command, PmChatCommand):
        return PmChatResult(success=False, message="指令類型錯誤", error_code="bad_command")
    text = command.text.strip()
    if not text:
        return PmChatResult(success=False, message="訊息不可為空白", error_code="invalid_text")
    try:
        project_id = require_active_project_id(deps.workspace_root, None)
    except ValueError as exc:
        return PmChatResult(success=False, message=str(exc), error_code="no_active_project")
    file_store.ensure_company_dirs(deps.workspace_root)
    global_config = file_store.load_global_config(deps.workspace_root)
    ai_core.configure_generation(app_settings.resolve_ai_generation(global_config))
    model = app_settings.resolve_model(global_config)
    generation = ai_core.current_generation()
    backend = ai_core.get_chat_backend(deps.settings)
    try:
        record = _ensure_pm_handle(
            deps, backend, project_id, model=model, generation=generation
        )
        reply, _ = _send_with_recovery(
            deps,
            backend,
            project_id,
            record,
            text,
            model=model,
            generation=generation,
        )
    except Exception as exc:
        return PmChatResult(
            success=False,
            message=f"PM 對話失敗：{exc}",
            error_code="pm_chat_failed",
        )
    record_chat_usage(
        deps.workspace_root,
        event="pm_chat",
        project_id=project_id,
        role="pm",
        user_text=text,
        reply_text=reply,
    )
    return PmChatResult(success=True, message=reply, reply=reply)


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.PM_CHAT,
        flow_id="pm_chat__work_flow",
        description_zh="PM Session 對話（綁定 active 專案）",
        runner=run,
    )
