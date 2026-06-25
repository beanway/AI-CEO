"""Harness 工具實作（list_skills、讀寫檔、終端）。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ai_company.modules.sandbox_runner import core as sandbox_runner
from ai_company.modules.sandbox_runner.core import ToolPolicyError
from ai_company.schemas.workspace_paths import project_dir


@dataclass
class HarnessToolContext:
    workspace_root: Path
    project_id: str
    worker_id: str
    files_changed: list[str] = field(default_factory=list)


def list_skills(ctx: HarnessToolContext) -> str:
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


def read_skill(ctx: HarnessToolContext, skill_file: str) -> str:
    if "/" in skill_file or ".." in skill_file or not skill_file.endswith(".md"):
        raise ToolPolicyError(f"不允許的 skill 檔名：{skill_file!r}")
    rel = f"workers/{ctx.worker_id}/skills/{skill_file}"
    return sandbox_runner.read_file_in_backend_sandbox(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, rel
    )


def read_file(ctx: HarnessToolContext, path: str) -> str:
    return sandbox_runner.read_file_in_backend_sandbox(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, path
    )


def write_file(ctx: HarnessToolContext, path: str, content: str) -> str:
    sandbox_runner.write_file_in_backend_sandbox(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, path, content
    )
    if path not in ctx.files_changed:
        ctx.files_changed.append(path)
    return json.dumps({"ok": True, "path": path}, ensure_ascii=False)


def run_terminal(ctx: HarnessToolContext, argv: list[str]) -> str:
    result = sandbox_runner.run_argv_in_worker_cwd(
        ctx.workspace_root, ctx.project_id, ctx.worker_id, argv
    )
    return json.dumps(
        {
            "returncode": result.returncode,
            "stdout": result.stdout[-8000:],
            "stderr": result.stderr[-8000:],
        },
        ensure_ascii=False,
    )


TOOL_NAMES = frozenset(
    {"list_skills", "read_skill", "read_file", "write_file", "run_terminal", "complete_task"}
)


def dispatch_tool(ctx: HarnessToolContext, name: str, args: dict) -> str:
    if name not in TOOL_NAMES:
        raise ToolPolicyError(f"未知工具：{name!r}")
    if name == "list_skills":
        return list_skills(ctx)
    if name == "read_skill":
        return read_skill(ctx, str(args.get("skill_file", "")))
    if name == "read_file":
        return read_file(ctx, str(args.get("path", "")))
    if name == "write_file":
        return write_file(ctx, str(args.get("path", "")), str(args.get("content", "")))
    if name == "run_terminal":
        raw = args.get("argv")
        if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
            raise ToolPolicyError("run_terminal 需要 argv: string[]")
        return run_terminal(ctx, raw)
    if name == "complete_task":
        return json.dumps(args, ensure_ascii=False)
    raise ToolPolicyError(f"未實作工具：{name}")
