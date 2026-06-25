"""Backend Worker agent 迴圈（僅依賴 host 注入的 session）。"""

from __future__ import annotations

import json
from typing import Any, Protocol


class BackendHostSession(Protocol):
  workspace_root: Any
  project_id: str
  worker_id: str
  files_changed: list[str]

  def dispatch_tool(self, name: str, args: dict) -> str: ...

  def load_task(self) -> dict: ...

  def complete_task(self, task: dict, args: dict) -> dict: ...

  def fail_task(self, task: dict, summary: str, turns: int) -> dict: ...


def _tool_calls_from_turn(turn: Any) -> list[tuple[str, dict]]:
  if hasattr(turn, "tool_calls"):
    return [(tc.name, tc.args) for tc in turn.tool_calls]
  tool_calls = turn.get("tool_calls") if isinstance(turn, dict) else None
  if not tool_calls:
    return []
  out: list[tuple[str, dict]] = []
  for tc in tool_calls:
    if hasattr(tc, "name"):
      out.append((tc.name, tc.args))
    else:
      out.append((tc["name"], tc["args"]))
  return out


def run_scripted_loop(
  session: BackendHostSession,
  turns: list[Any],
  *,
  max_turns: int = 25,
) -> dict:
  task = session.load_task()
  turn_iter = iter(turns)
  last_error: str | None = None
  turns_used = 0

  while turns_used < max_turns:
    turns_used += 1
    try:
      turn = next(turn_iter)
    except StopIteration:
      last_error = "Agent 無後續步驟"
      break

    text = getattr(turn, "text", None) if not isinstance(turn, dict) else turn.get("text")
    tool_calls = _tool_calls_from_turn(turn)
    if text and not tool_calls:
      last_error = str(text)
      break
    if not tool_calls:
      last_error = last_error or "模型未回傳工具呼叫"
      break

    for name, args in tool_calls:
      if name == "complete_task":
        result = session.complete_task(task, args)
        result["turns_used"] = turns_used
        return result
      session.dispatch_tool(name, args)

  return session.fail_task(task, last_error or "超過最大輪次", turns_used)


def run_execution_step(session: BackendHostSession) -> dict:
  """run-step 無 LLM 時：確認 package 可載入並寫入最小 last_run。"""
  task = session.load_task()
  return session.complete_task(
    task,
    {
      "status": "success",
      "summary": "worker package execution_step（無 LLM）",
      "test_command": "",
      "test_exit_code": 0,
    },
  )
