from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_company.modules.ai_core.internal.generation_config import build_generate_content_config
from ai_company.schemas.ai_generation import AiGenerationSettings


@runtime_checkable
class ChatBackend(Protocol):
    def create_chat(
        self,
        *,
        system_instruction: str,
        model: str,
        generation: AiGenerationSettings,
    ) -> str: ...

    def send_message(self, chat_name: str, text: str, *, model: str) -> str: ...

    def has_chat(self, chat_name: str) -> bool: ...


class FakeChatBackend:
    """本機／測試用：記憶體內保留對話脈絡。"""

    def __init__(self) -> None:
        self._chats: dict[str, list[str]] = {}
        self._counter = 0

    def create_chat(
        self,
        *,
        system_instruction: str,
        model: str,
        generation: AiGenerationSettings,
    ) -> str:
        del model, generation
        self._counter += 1
        name = f"fake-chat-{self._counter}"
        self._chats[name] = [system_instruction]
        return name

    def send_message(self, chat_name: str, text: str, *, model: str) -> str:
        del model
        if chat_name not in self._chats:
            raise KeyError(chat_name)
        self._chats[chat_name].append(text)
        return f"[fake CEO 回覆] 已收到：{text}"

    def has_chat(self, chat_name: str) -> bool:
        return chat_name in self._chats


class GeminiChatBackend:
    """Google Genai SDK；chat 物件僅存於程序記憶體。"""

    def __init__(self, api_key: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._chats: dict[str, object] = {}
        self._counter = 0

    def create_chat(
        self,
        *,
        system_instruction: str,
        model: str,
        generation: AiGenerationSettings,
    ) -> str:
        config = build_generate_content_config(
            system_instruction=system_instruction,
            generation=generation,
        )
        chat = self._client.chats.create(model=model, config=config)
        self._counter += 1
        name = f"gemini-{self._counter}-{id(chat)}"
        self._chats[name] = chat
        return name

    def send_message(self, chat_name: str, text: str, *, model: str) -> str:
        del model
        chat = self._chats.get(chat_name)
        if chat is None:
            raise KeyError(chat_name)
        response = chat.send_message(text)
        return (response.text or "").strip()

    def send_message_with_metadata(
        self, chat_name: str, text: str, *, model: str
    ) -> tuple[str, object | None]:
        """供診斷腳本使用；正式 flow 仍用 send_message。"""
        del model
        chat = self._chats.get(chat_name)
        if chat is None:
            raise KeyError(chat_name)
        response = chat.send_message(text)
        usage = getattr(response, "usage_metadata", None)
        return (response.text or "").strip(), usage

    def has_chat(self, chat_name: str) -> bool:
        return chat_name in self._chats
