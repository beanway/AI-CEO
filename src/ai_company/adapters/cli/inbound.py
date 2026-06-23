"""CLI argv → Command → dispatch."""

from __future__ import annotations

import sys

from ai_company.adapters.deps import AppDeps
from ai_company.adapters.dispatch import dispatch
from ai_company.config import get_settings
from ai_company.schemas.commands import (
    Channel,
    InitWorkspaceCommand,
    ListProjectsCommand,
    ShowGlobalConfigCommand,
    SwitchProjectCommand,
)


def run_init_workspace() -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(InitWorkspaceCommand(channel=Channel.CLI), deps)
    print(result.message)
    return 0 if result.success else 1


def run_projects() -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(ListProjectsCommand(channel=Channel.CLI), deps)
    print(result.message)
    return 0 if result.success else 1


def run_switch(project_id: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        SwitchProjectCommand(channel=Channel.CLI, project_id=project_id),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_global() -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(ShowGlobalConfigCommand(channel=Channel.CLI), deps)
    print(result.message)
    return 0 if result.success else 1
