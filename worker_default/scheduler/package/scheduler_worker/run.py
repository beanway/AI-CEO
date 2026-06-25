from __future__ import annotations

from typing import Any

from scheduler_worker.engine import run_execution_step as _run_execution_step
from scheduler_worker.engine import run_scripted_loop


def run_scripted(session: Any, turns: list[Any], *, max_turns: int = 25) -> dict:
  return run_scripted_loop(session, turns, max_turns=max_turns)


def run_execution_step(session: Any) -> dict:
  return _run_execution_step(session)
