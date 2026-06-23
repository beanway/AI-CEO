"""對齊 google-genai GenerateContentConfig（官網 / SDK 文件）。"""

from __future__ import annotations

from google.genai import types


def build_generate_content_config(
    *,
    system_instruction: str,
    max_output_tokens: int = 8192,
    temperature: float | None = None,
    thinking_budget: int = 0,
    include_thoughts: bool = False,
) -> types.GenerateContentConfig:
    """
    - system_instruction：chats.create 的 config（官網 System Instructions）
    - max_output_tokens：拉長可見回覆（預設 8192）
    - thinking_budget=0：關閉延伸 thinking 預算（thinking 模型適用）
    - include_thoughts：False 時 response.text 不含思考過程
    """
    thinking = types.ThinkingConfig(
        thinking_budget=thinking_budget,
        include_thoughts=include_thoughts,
    )
    kwargs: dict = {
        "system_instruction": system_instruction,
        "max_output_tokens": max_output_tokens,
        "thinking_config": thinking,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    return types.GenerateContentConfig(**kwargs)
