"""Work flow package: import _register to load all flow registrations."""

from __future__ import annotations

from ai_company.app_deps import AppDeps
from ai_company.schemas.commands import BaseCommand
from ai_company.schemas.results import FlowResult
from ai_company.work_flow import _register  # noqa: F401
from ai_company.work_flow.registry import registry


def dispatch(command: BaseCommand, deps: AppDeps) -> FlowResult:
    return registry.run(command, deps)
