"""AI 供應商、模型解析與對話 backend。"""

from __future__ import annotations

from ai_company.config import Settings
from ai_company.modules.ai_core.internal.backends import (
    ChatBackend,
    FakeChatBackend,
    GeminiChatBackend,
)
from ai_company.schemas.documents import GlobalConfigFile

CEO_SYSTEM_INSTRUCTION = (
    "你是 AI 公司的執行長（CEO）。協助使用者確認商業模式與需求，可建議建立專案。"
    "全公司設定在 global_config / global_skills；專案列表與切換由使用者透過"
    " /projects、/switch、/newproject 或你引導完成。"
)

_backends: dict[str, ChatBackend] = {}


def resolve_model(
    settings: Settings,
    global_config: GlobalConfigFile | None = None,
) -> str:
    del settings
    if global_config is not None and global_config.default_model.strip():
        return global_config.default_model.strip()
    return "gemini-2.5-flash"


def get_chat_backend(settings: Settings) -> ChatBackend:
    key = (
        f"gemini:{settings.gemini_api_key.strip()[:12]}"
        if settings.gemini_api_key.strip()
        else "fake"
    )
    backend = _backends.get(key)
    if backend is not None:
        return backend
    if settings.gemini_api_key.strip():
        backend = GeminiChatBackend(settings.gemini_api_key.strip())
    else:
        backend = FakeChatBackend()
    _backends[key] = backend
    return backend


def reset_chat_backends_for_tests() -> None:
    """僅供 pytest 隔離程序內 singleton。"""
    _backends.clear()
