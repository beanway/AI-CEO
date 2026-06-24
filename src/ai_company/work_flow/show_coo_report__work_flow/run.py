from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.modules.metrics import core as metrics
from ai_company.schemas.commands import BaseCommand, CommandType, ShowCooReportCommand
from ai_company.schemas.results import ShowCooReportResult
from ai_company.work_flow.registry import WorkFlowRegistry


def run(command: BaseCommand, deps: AppDeps) -> ShowCooReportResult:
    if not isinstance(command, ShowCooReportCommand):
        return ShowCooReportResult(
            success=False, message="指令類型錯誤", error_code="bad_command"
        )
    summary = metrics.summarize_usage(deps.workspace_root)
    event_lines = (
        "\n".join(f"  {k}: {v} 次" for k, v in sorted(summary.by_event.items()))
        or "  （無）"
    )
    project_lines = (
        "\n".join(f"  {k}: ~{v} tokens" for k, v in sorted(summary.by_project.items()))
        or "  （無）"
    )
    message = (
        "COO 用量報表（usage.jsonl）\n"
        f"事件總數：{summary.total_events}\n"
        f"估計 tokens 合計：{summary.total_tokens_estimated}\n"
        f"依 event：\n{event_lines}\n"
        f"依 project（tokens）：\n{project_lines}"
    )
    return ShowCooReportResult(
        success=True,
        message=message,
        total_events=summary.total_events,
        total_tokens_estimated=summary.total_tokens_estimated,
    )


def register(registry: WorkFlowRegistry) -> None:
    registry.register(
        CommandType.SHOW_COO_REPORT,
        flow_id="show_coo_report__work_flow",
        description_zh="COO 用量報表（metrics/usage.jsonl）",
        runner=run,
    )
