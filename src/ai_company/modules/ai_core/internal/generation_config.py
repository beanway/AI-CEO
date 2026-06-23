"""對齊 google-genai GenerateContentConfig（官網 / SDK 文件）。"""

from __future__ import annotations

from google.genai import types

from ai_company.schemas.ai_generation import AiGenerationSettings


def build_generate_content_config(
    *,
    system_instruction: str,
    generation: AiGenerationSettings,
) -> types.GenerateContentConfig:
    thinking = types.ThinkingConfig(
        thinking_budget=generation.thinking_budget,
        include_thoughts=generation.include_thoughts,
    )
    kwargs: dict = {
        "system_instruction": system_instruction,
        "max_output_tokens": generation.max_output_tokens,
        "thinking_config": thinking,
    }
    if generation.temperature is not None:
        kwargs["temperature"] = generation.temperature
    return types.GenerateContentConfig(**kwargs)
