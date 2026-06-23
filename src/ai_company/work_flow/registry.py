"""Unified work_flow registration and dispatch."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from ai_company.app_deps import AppDeps
from ai_company.schemas.commands import BaseCommand, CommandType
from ai_company.schemas.results import FlowResult

C = TypeVar("C", bound=BaseCommand)
R = TypeVar("R", bound=FlowResult)

FlowRunner = Callable[[BaseCommand, AppDeps], FlowResult]


@dataclass(frozen=True)
class FlowRegistration:
    command_type: CommandType
    flow_id: str
    description_zh: str


class WorkFlowRegistry:
    def __init__(self) -> None:
        self._runners: dict[CommandType, FlowRunner] = {}
        self._meta: dict[CommandType, FlowRegistration] = {}

    def register(
        self,
        command_type: CommandType,
        flow_id: str,
        description_zh: str,
        runner: FlowRunner,
    ) -> None:
        if command_type in self._runners and self._meta[command_type].flow_id != flow_id:
            raise ValueError(f"command_type already registered: {command_type}")
        self._runners[command_type] = runner
        self._meta[command_type] = FlowRegistration(
            command_type=command_type,
            flow_id=flow_id,
            description_zh=description_zh,
        )

    def run(self, command: BaseCommand, deps: AppDeps) -> FlowResult:
        runner = self._runners.get(command.command_type)
        if runner is None:
            return FlowResult(
                success=False,
                message=f"未註冊的流程：{command.command_type}",
                error_code="flow_not_registered",
            )
        return runner(command, deps)

    def list_flows(self) -> list[FlowRegistration]:
        return [self._meta[k] for k in sorted(self._meta, key=lambda x: x.value)]


registry = WorkFlowRegistry()
