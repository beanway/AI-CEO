"""Gemini function-calling 驅動 Worker 迴圈。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types

from ai_company.modules.ai_core import core as ai_core
from ai_company.schemas.ai_generation import AiGenerationSettings

WORKER_TOOL_DECLARATIONS: list[types.FunctionDeclaration] = [
    types.FunctionDeclaration(
        name="list_skills",
        description="列出 workers/<id>/skills/ 下可用的 .md 技能劇本檔名。",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="read_skill",
        description="讀取單一技能劇本全文。",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "skill_file": types.Schema(
                    type=types.Type.STRING,
                    description="檔名，例如 01_plan_implement_test.md",
                ),
            },
            required=["skill_file"],
        ),
    ),
    types.FunctionDeclaration(
        name="read_file",
        description="讀取專案沙盒內相對路徑檔案。",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"path": types.Schema(type=types.Type.STRING)},
            required=["path"],
        ),
    ),
    types.FunctionDeclaration(
        name="write_file",
        description="寫入專案沙盒內相對路徑檔案。",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "path": types.Schema(type=types.Type.STRING),
                "content": types.Schema(type=types.Type.STRING),
            },
            required=["path", "content"],
        ),
    ),
    types.FunctionDeclaration(
        name="run_terminal",
        description="在專案根 cwd 執行白名單指令（pytest、python3 -m pytest、ruff）。",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "argv": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                ),
            },
            required=["argv"],
        ),
    ),
    types.FunctionDeclaration(
        name="complete_task",
        description="任務結束；success 時 test_exit_code 必須為 0。",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "status": types.Schema(
                    type=types.Type.STRING,
                    description="success 或 failed",
                ),
                "summary": types.Schema(type=types.Type.STRING),
                "test_command": types.Schema(type=types.Type.STRING),
                "test_exit_code": types.Schema(type=types.Type.INTEGER),
                "notes_for_reviewer": types.Schema(type=types.Type.STRING),
            },
            required=["status", "summary", "test_command", "test_exit_code"],
        ),
    ),
]


@dataclass
class GeminiTurn:
    tool_calls: list[tuple[str, dict]]
    text: str | None


class GeminiAgentDriver:
    def __init__(self, api_key: str, *, model: str, generation: AiGenerationSettings) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._generation = generation
        self._contents: list[types.Content] = []
        self._system = ""

    def start(self, system_instruction: str, user_task: str) -> None:
        self._system = system_instruction
        self._contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_task)],
            )
        ]

    def next_turn(self) -> GeminiTurn:
        config = ai_core.build_generate_content_config(
            system_instruction=self._system,
            generation=self._generation,
        )
        config.tools = [types.Tool(function_declarations=WORKER_TOOL_DECLARATIONS)]

        response = self._client.models.generate_content(
            model=self._model,
            contents=self._contents,
            config=config,
        )

        tool_calls: list[tuple[str, dict]] = []
        text_parts: list[str] = []

        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                self._contents.append(candidate.content)
                for part in candidate.content.parts:
                    if part.text:
                        text_parts.append(part.text)
                    fc = part.function_call
                    if fc and fc.name:
                        args = dict(fc.args) if fc.args else {}
                        tool_calls.append((fc.name, args))

        return GeminiTurn(
            tool_calls=tool_calls,
            text="\n".join(text_parts).strip() or None,
        )

    def submit_tool_results(self, results: list[tuple[str, Any]]) -> None:
        parts = [
            types.Part.from_function_response(name=name, response={"result": result})
            for name, result in results
        ]
        self._contents.append(types.Content(role="user", parts=parts))
