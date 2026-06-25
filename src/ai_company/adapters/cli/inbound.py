"""CLI argv → Command → dispatch."""

from __future__ import annotations

import sys

from ai_company.adapters.deps import AppDeps
from ai_company.adapters.dispatch import dispatch
from ai_company.config import get_settings
from ai_company.schemas.commands import (
    UpdateGlobalConfigCommand,
    AddSkillToCompanyCommand,
    RemoveSkillFromCompanyCommand,
    AddSkillToProjectCommand,
    Channel,
    CeoChatCommand,
    CreateProjectCommand,
    InitWorkspaceCommand,
    ListProjectsCommand,
    PmChatCommand,
    SetUserModeCommand,
    SetupWorkersCommand,
    AddWorkerCommand,
    ShowGlobalConfigCommand,
    ShowProjectStatusCommand,
    SwitchProjectCommand,
    PmRepairCommand,
    PmResyncWorkerCommand,
    LoadFixtureScenarioCommand,
    ProjectGitCommand,
    RunExecutionStepCommand,
    ResolveExecutionFailureCommand,
    ListRegistrySkillsCommand,
    CreateRegistrySkillCommand,
    ShowCooReportCommand,
)
from ai_company.schemas.documents import UserMode


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


def run_remove_skill(skill_id: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        RemoveSkillFromCompanyCommand(channel=Channel.CLI, skill_id=skill_id),
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


CLI_TELEGRAM_USER_ID = 0


def run_mode(mode: str) -> int:
    if mode not in ("ceo", "pm"):
        print("用法：mode ceo|pm", file=sys.stderr)
        return 1
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        SetUserModeCommand(
            channel=Channel.CLI,
            telegram_user_id=CLI_TELEGRAM_USER_ID,
            mode=UserMode.PM if mode == "pm" else UserMode.CEO,
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_pm_chat(text: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(PmChatCommand(channel=Channel.CLI, text=text), deps)
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    reply = getattr(result, "reply", None) or result.message
    print(reply)
    return 0


def run_setup_workers(template: str) -> int:
    if template not in ("five", "three"):
        print("template 須為 five 或 three", file=sys.stderr)
        return 1
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        SetupWorkersCommand(channel=Channel.CLI, template=template),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_add_worker(template: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        AddWorkerCommand(channel=Channel.CLI, template=template.strip().lower()),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_project_status() -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(ShowProjectStatusCommand(channel=Channel.CLI), deps)
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_add_project_skill(skill_id: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        AddSkillToProjectCommand(channel=Channel.CLI, skill_id=skill_id),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_project_git(git_argv: list[str]) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        ProjectGitCommand(channel=Channel.CLI, git_argv=git_argv),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_pm_repair(*, interrupt: bool) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        PmRepairCommand(channel=Channel.CLI, interrupt=interrupt),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_resync_worker(template: str, *, keep_package: bool = False) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        PmResyncWorkerCommand(
            channel=Channel.CLI,
            template=template.strip().lower(),
            force_package=not keep_package,
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_load_fixture_scenario(scenario: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        LoadFixtureScenarioCommand(
            channel=Channel.CLI,
            scenario=scenario.strip(),
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_execution_step(*, simulate_failure: bool = False) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        RunExecutionStepCommand(
            channel=Channel.CLI,
            simulate_failure=simulate_failure,
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_resolve_execution_failure(failure_id: str, decision: str) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        ResolveExecutionFailureCommand(
            channel=Channel.CLI,
            failure_id=failure_id,
            decision=decision,  # type: ignore[arg-type]
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_list_registry_skills(query: str | None = None) -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        ListRegistrySkillsCommand(channel=Channel.CLI, query=query),
        deps,
    )
    print(result.message)
    return 0 if result.success else 1


def run_create_registry_skill(skill_id: str, description: str = "") -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(
        CreateRegistrySkillCommand(
            channel=Channel.CLI,
            skill_id=skill_id,
            description=description,
        ),
        deps,
    )
    if not result.success:
        print(result.message, file=sys.stderr)
        return 1
    print(result.message)
    return 0


def run_coo_report() -> int:
    deps = AppDeps(settings=get_settings())
    result = dispatch(ShowCooReportCommand(channel=Channel.CLI), deps)
    print(result.message)
    return 0 if result.success else 1
