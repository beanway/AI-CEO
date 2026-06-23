"""可重用工具模組：回覆排版（DTO/Result → 字串）。"""

from __future__ import annotations

from ai_company.models.company import ProjectsFile


def format_projects_message(pf: ProjectsFile) -> str:
    lines = [f"Active: {pf.active_project_id or '（無）'}"]
    if not pf.projects:
        lines.append("（尚無專案）")
    else:
        for p in pf.projects:
            mark = " *" if p.id == pf.active_project_id else ""
            lines.append(f"- {p.id}{mark}: {p.name}")
    return "\n".join(lines)
