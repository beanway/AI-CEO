"""測試用：依序回傳預定 tool calls。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedToolCall:
    name: str
    args: dict


@dataclass
class ScriptedAgentTurn:
    tool_calls: list[PlannedToolCall]
    text: str | None = None


class ScriptedAgentDriver:
    def __init__(self, turns: list[ScriptedAgentTurn]) -> None:
        self._turns = list(turns)
        self._index = 0

    def consume_turn(self) -> ScriptedAgentTurn | None:
        if self._index >= len(self._turns):
            return None
        turn = self._turns[self._index]
        self._index += 1
        return turn
