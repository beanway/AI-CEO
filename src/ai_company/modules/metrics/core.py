"""COO 用量紀錄與彙總（usage.jsonl）。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_company.schemas.documents import UsageMetricRecord, utc_now


def metrics_dir(workspace_root: Path) -> Path:
    return workspace_root / "_company" / "metrics"


def usage_log_path(workspace_root: Path) -> Path:
    return metrics_dir(workspace_root) / "usage.jsonl"


def append_usage(workspace_root: Path, record: UsageMetricRecord) -> None:
    directory = metrics_dir(workspace_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = usage_log_path(workspace_root)
    line = record.model_dump_json()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def append_usage_event(
    workspace_root: Path,
    *,
    event: str,
    project_id: str | None = None,
    role: str | None = None,
    tokens_estimated: int = 0,
    detail: str = "",
) -> None:
    append_usage(
        workspace_root,
        UsageMetricRecord(
            event=event,
            project_id=project_id,
            role=role,
            tokens_estimated=tokens_estimated,
            detail=detail,
        ),
    )


def load_usage_records(workspace_root: Path) -> list[UsageMetricRecord]:
    path = usage_log_path(workspace_root)
    if not path.is_file():
        return []
    records: list[UsageMetricRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(UsageMetricRecord.model_validate_json(line))
        except json.JSONDecodeError:
            continue
    return records


@dataclass(frozen=True)
class UsageSummary:
    total_events: int
    total_tokens_estimated: int
    by_event: dict[str, int]
    by_project: dict[str, int]


def summarize_usage(workspace_root: Path) -> UsageSummary:
    records = load_usage_records(workspace_root)
    by_event: dict[str, int] = {}
    by_project: dict[str, int] = {}
    tokens = 0
    for rec in records:
        by_event[rec.event] = by_event.get(rec.event, 0) + 1
        tokens += rec.tokens_estimated
        if rec.project_id:
            by_project[rec.project_id] = by_project.get(rec.project_id, 0) + rec.tokens_estimated
    return UsageSummary(
        total_events=len(records),
        total_tokens_estimated=tokens,
        by_event=by_event,
        by_project=by_project,
    )


def estimate_tokens(*parts: str) -> int:
    text = "".join(parts)
    return max(1, len(text) // 4) if text else 0
