"""AI 供應商、模型解析與對話 backend。"""

from __future__ import annotations

from ai_company.modules.ai_core.internal.backends import (
    ChatBackend,
    FakeChatBackend,
    GeminiChatBackend,
)
from ai_company.modules.settings.core import AppSettings
from ai_company.schemas.ai_generation import AiGenerationSettings

CEO_SYSTEM_INSTRUCTION = (
    "你是 AI 公司的執行長（CEO）。協助使用者確認商業模式與需求，可建議建立專案。"
    "全公司設定在 global_config / global_skills；專案列表與切換由使用者透過"
    " /projects、/switch、/newproject 或你引導完成。"
)

_backends: dict[str, ChatBackend] = {}
_generation: AiGenerationSettings = AiGenerationSettings()


def configure_generation(settings: AiGenerationSettings) -> None:
    """在建立／使用 Gemini chat 前套用（通常由 work_flow 從 global_config 解析）。"""
    global _generation
    _generation = settings


def current_generation() -> AiGenerationSettings:
    return _generation


def get_chat_backend(app_settings: AppSettings) -> ChatBackend:
    api_key = app_settings.resolved_gemini_api_key()
    cache_key = f"gemini:{api_key[:12]}" if api_key else "fake"
    backend = _backends.get(cache_key)
    if backend is not None:
        return backend
    if api_key:
        backend = GeminiChatBackend(api_key)
    else:
        backend = FakeChatBackend()
    _backends[cache_key] = backend
    return backend


def reset_chat_backends_for_tests() -> None:
    """僅供 pytest 隔離程序內 singleton。"""
    global _generation
    _backends.clear()
    _generation = AiGenerationSettings()
