"""記錄 chat 用量至 COO metrics。"""

from __future__ import annotations

from pathlib import Path

from ai_company.modules.metrics import core as metrics


def record_chat_usage(
    workspace_root: Path,
    *,
    event: str,
    project_id: str | None,
    role: str,
    user_text: str,
    reply_text: str,
) -> None:
    tokens = metrics.estimate_tokens(user_text, reply_text)
    metrics.append_usage_event(
        workspace_root,
        event=event,
        project_id=project_id,
        role=role,
        tokens_estimated=tokens,
        detail=f"in={len(user_text)} out={len(reply_text)}",
    )
