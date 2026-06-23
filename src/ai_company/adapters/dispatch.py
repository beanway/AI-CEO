"""Adapter entry: dispatch commands to work_flow.registry."""

from ai_company.adapters.deps import AppDeps
from ai_company.schemas.commands import BaseCommand
from ai_company.schemas.results import FlowResult
from ai_company.work_flow import dispatch as workflow_dispatch


def dispatch(command: BaseCommand, deps: AppDeps) -> FlowResult:
    return workflow_dispatch(command, deps)
