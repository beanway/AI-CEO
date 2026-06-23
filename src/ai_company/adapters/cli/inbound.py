"""CLI argv → Command → dispatch."""

from __future__ import annotations

import sys

from ai_company.adapters.deps import AppDeps
from ai_company.adapters.dispatch import dispatch
from ai_company.config import get_settings
from ai_company.schemas.commands import (
    UpdateGlobalConfigCommand,
    AddSkillToCompanyCommand,
    Channel,
    CeoChatCommand,
    CreateProjectCommand,
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


def run_create_project(name: str, *, initial_requirements: str | None = None) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        CreateProjectCommand(
            channel=Channel.CLI,
            name=name,
            initial_requirements=initial_requirements,
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


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


def run_add_skill(skill_id: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        AddSkillToCompanyCommand(channel=Channel.CLI, skill_id=skill_id),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_update_global_config(
    *,
    default_model: str | None = None,
    notification_policy: str | None = None,
    max_output_tokens: int | None = None,
    thinking_budget: int | None = None,
    include_thoughts: bool | None = None,
    temperature: float | None = None,
) -> int:
    from ai_company.schemas.documents import NotificationPolicy

    policy = None
    if notification_policy is not None:
        try:
            policy = NotificationPolicy(notification_policy.strip().lower())
        except ValueError:
            print(f"無效的 notification_policy: {notification_policy}", file=sys.stderr)
            return 1
    try:
        command = UpdateGlobalConfigCommand(
            channel=Channel.CLI,
            default_model=default_model,
            notification_policy=policy,
            max_output_tokens=max_output_tokens,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts,
            temperature=temperature,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    deps = AppDeps(settings=get_settings())
    result = dispatch(command, deps)
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_ceo_chat(text: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(CeoChatCommand(channel=Channel.CLI, text=text), deps)
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    reply = getattr(result, "reply", None) or result.message
    print(reply)
    return 0
