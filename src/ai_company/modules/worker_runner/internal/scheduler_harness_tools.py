"""任務分配者 harness 工具（讀寫 pm/、規劃產物）。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ai_company.modules.sandbox_runner.core import (
    ToolPolicyError,
    validate_scheduler_relative_path,
)
from ai_company.schemas.workspace_paths import project_dir


@dataclass
class SchedulerHarnessToolContext:
    workspace_root: Path
    project_id: str
    worker_id: str
    files_changed: list[str] = field(default_factory=list)


def _read_text(ctx: SchedulerHarnessToolContext, rel_path: str) -> str:
    path = validate_scheduler_relative_path(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, rel_path, for_write=False
    )
    if not path.is_file():
        raise ToolPolicyError(f"檔案不存在：{rel_path!r}")
    return path.read_text(encoding="utf-8")


def _write_text(ctx: SchedulerHarnessToolContext, rel_path: str, content: str) -> None:
    path = validate_scheduler_relative_path(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, rel_path, for_write=True
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if rel_path not in ctx.files_changed:
        ctx.files_changed.append(rel_path)


def list_skills(ctx: SchedulerHarnessToolContext) -> str:
    skills_dir = (
        project_dir(ctx.workspace_root, ctx.project_id)
        / "workers"
        / ctx.worker_id
        / "skills"
    )
    if not skills_dir.is_dir():
        return json.dumps({"skills": []}, ensure_ascii=False)
    names = sorted(p.name for p in skills_dir.iterdir() if p.suffix == ".md" and p.is_file())
    return json.dumps({"skills": names}, ensure_ascii=False)


def read_skill(ctx: SchedulerHarnessToolContext, skill_file: str) -> str:
    if "/" in skill_file or ".." in skill_file or not skill_file.endswith(".md"):
        raise ToolPolicyError(f"不允許的 skill 檔名：{skill_file!r}")
    rel = f"workers/{ctx.worker_id}/skills/{skill_file}"
    return _read_text(ctx, rel)


def read_file(ctx: SchedulerHarnessToolContext, path: str) -> str:
    return _read_text(ctx, path)


def write_file(ctx: SchedulerHarnessToolContext, path: str, content: str) -> str:
    _write_text(ctx, path, content)
    return json.dumps({"ok": True, "path": path}, ensure_ascii=False)


SCHEDULER_TOOL_NAMES = frozenset(
    {"list_skills", "read_skill", "read_file", "write_file", "complete_task"}
)


def dispatch_scheduler_tool(ctx: SchedulerHarnessToolContext, name: str, args: dict) -> str:
    if name not in SCHEDULER_TOOL_NAMES:
        raise ToolPolicyError(f"未知工具：{name!r}")
    if name == "list_skills":
        return list_skills(ctx)
    if name == "read_skill":
        return read_skill(ctx, str(args.get("skill_file", "")))
    if name == "read_file":
        return read_file(ctx, str(args.get("path", "")))
    if name == "write_file":
        return write_file(ctx, str(args.get("path", "")), str(args.get("content", "")))
    if name == "complete_task":
        return json.dumps(args, ensure_ascii=False)
    raise ToolPolicyError(f"未實作工具：{name!r}")
