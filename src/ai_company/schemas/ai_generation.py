"""AI 生成參數 DTO（env + global_config 解析後供 ai_core 使用）。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AiGenerationSettings(BaseModel):
    max_output_tokens: int = Field(default=8192, ge=1)
    thinking_budget: int = 0
    include_thoughts: bool = False
    temperature: float | None = None
