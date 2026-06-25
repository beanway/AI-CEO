"""Inbound commands: adapters → work_flow (discriminated by command_type)."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ai_company.schemas.documents import NotificationPolicy, UserMode, WorkerEntry


class CommandType(str, Enum):
    INIT_WORKSPACE = "init_workspace"
    LIST_PROJECTS = "list_projects"
    SWITCH_PROJECT = "switch_project"
    CREATE_PROJECT = "create_project"
    CEO_CHAT = "ceo_chat"
    SHOW_GLOBAL_CONFIG = "show_global_config"
    ADD_SKILL_TO_COMPANY = "add_skill_to_company"
    REMOVE_SKILL_FROM_COMPANY = "remove_skill_from_company"
    UPDATE_GLOBAL_CONFIG = "update_global_config"
    SET_USER_MODE = "set_user_mode"
    PM_CHAT = "pm_chat"
    SETUP_WORKERS = "setup_workers"
    ADD_WORKER = "add_worker"
    ADD_SKILL_TO_PROJECT = "add_skill_to_project"
    SHOW_PROJECT_STATUS = "show_project_status"
    PROJECT_GIT = "project_git"
    RESOLVE_APPROVAL = "resolve_approval"
    PM_REPAIR = "pm_repair"
    RUN_EXECUTION_STEP = "run_execution_step"
    RESOLVE_EXECUTION_FAILURE = "resolve_execution_failure"
    LIST_REGISTRY_SKILLS = "list_registry_skills"
    CREATE_REGISTRY_SKILL = "create_registry_skill"
    SHOW_COO_REPORT = "show_coo_report"
    ROUTE_MANAGER_CHAT = "route_manager_chat"


class Channel(str, Enum):
    TELEGRAM = "telegram"
    CLI = "cli"
    WEB = "web"


class BaseCommand(BaseModel):
    command_type: CommandType
    channel: Channel = Channel.CLI


class InitWorkspaceCommand(BaseCommand):
    command_type: Literal[CommandType.INIT_WORKSPACE] = CommandType.INIT_WORKSPACE


class ListProjectsCommand(BaseCommand):
    command_type: Literal[CommandType.LIST_PROJECTS] = CommandType.LIST_PROJECTS


class SwitchProjectCommand(BaseCommand):
    command_type: Literal[CommandType.SWITCH_PROJECT] = CommandType.SWITCH_PROJECT
    project_id: str = Field(min_length=1)


class CreateProjectCommand(BaseCommand):
    command_type: Literal[CommandType.CREATE_PROJECT] = CommandType.CREATE_PROJECT
    name: str = Field(min_length=1)
    initial_requirements: str | None = None


class CeoChatCommand(BaseCommand):
    command_type: Literal[CommandType.CEO_CHAT] = CommandType.CEO_CHAT
    text: str = Field(min_length=1)


class ShowGlobalConfigCommand(BaseCommand):
    command_type: Literal[CommandType.SHOW_GLOBAL_CONFIG] = CommandType.SHOW_GLOBAL_CONFIG


class AddSkillToCompanyCommand(BaseCommand):
    command_type: Literal[CommandType.ADD_SKILL_TO_COMPANY] = CommandType.ADD_SKILL_TO_COMPANY
    skill_id: str = Field(min_length=1)


class RemoveSkillFromCompanyCommand(BaseCommand):
    command_type: Literal[CommandType.REMOVE_SKILL_FROM_COMPANY] = (
        CommandType.REMOVE_SKILL_FROM_COMPANY
    )
    skill_id: str = Field(min_length=1)


class UpdateGlobalConfigCommand(BaseCommand):
    command_type: Literal[CommandType.UPDATE_GLOBAL_CONFIG] = CommandType.UPDATE_GLOBAL_CONFIG
    default_model: str | None = None
    notification_policy: NotificationPolicy | None = None
    max_output_tokens: int | None = Field(default=None, ge=1)
    thinking_budget: int | None = None
    include_thoughts: bool | None = None
    temperature: float | None = None
    executor_notify_chat_id: int | None = None
    dispatch_min_score: int | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def at_least_one_field(self) -> UpdateGlobalConfigCommand:
        if self.default_model is None and self.notification_policy is None:
            if self.max_output_tokens is None and self.thinking_budget is None:
                if self.include_thoughts is None and self.temperature is None:
                    if self.executor_notify_chat_id is None and self.dispatch_min_score is None:
                        raise ValueError("至少需提供一項 global_config 欄位")
        return self


class SetUserModeCommand(BaseCommand):
    command_type: Literal[CommandType.SET_USER_MODE] = CommandType.SET_USER_MODE
    telegram_user_id: int
    mode: UserMode


class PmChatCommand(BaseCommand):
    command_type: Literal[CommandType.PM_CHAT] = CommandType.PM_CHAT
    text: str = Field(min_length=1)


class SetupWorkersCommand(BaseCommand):
    command_type: Literal[CommandType.SETUP_WORKERS] = CommandType.SETUP_WORKERS
    project_id: str | None = None
    template: Literal["five", "three"] | None = None
    workers: list[WorkerEntry] | None = None

    @model_validator(mode="after")
    def template_xor_workers(self) -> SetupWorkersCommand:
        has_template = self.template is not None
        has_workers = self.workers is not None and len(self.workers) > 0
        if has_template == has_workers:
            raise ValueError("請指定 template（five|three）或 workers 列表，擇一")
        return self


class AddWorkerCommand(BaseCommand):
    """從 worker_default/<template>/ 加入單一 Worker（例：template=backend）。"""

    command_type: Literal[CommandType.ADD_WORKER] = CommandType.ADD_WORKER
    project_id: str | None = None
    template: str = Field(min_length=1)


class AddSkillToProjectCommand(BaseCommand):
    command_type: Literal[CommandType.ADD_SKILL_TO_PROJECT] = CommandType.ADD_SKILL_TO_PROJECT
    skill_id: str = Field(min_length=1)
    project_id: str | None = None
    telegram_user_id: int | None = None


class ShowProjectStatusCommand(BaseCommand):
    command_type: Literal[CommandType.SHOW_PROJECT_STATUS] = CommandType.SHOW_PROJECT_STATUS
    project_id: str | None = None


class ProjectGitCommand(BaseCommand):
    command_type: Literal[CommandType.PROJECT_GIT] = CommandType.PROJECT_GIT
    git_argv: list[str] = Field(min_length=1)
    project_id: str | None = None
    telegram_user_id: int | None = None


class ResolveApprovalCommand(BaseCommand):
    command_type: Literal[CommandType.RESOLVE_APPROVAL] = CommandType.RESOLVE_APPROVAL
    approval_id: str = Field(min_length=1)
    approved: bool
    telegram_user_id: int | None = None


class PmRepairCommand(BaseCommand):
    command_type: Literal[CommandType.PM_REPAIR] = CommandType.PM_REPAIR
    project_id: str | None = None
    interrupt: bool = False


class RunExecutionStepCommand(BaseCommand):
    command_type: Literal[CommandType.RUN_EXECUTION_STEP] = CommandType.RUN_EXECUTION_STEP
    project_id: str | None = None
    simulate_failure: bool = False


class ResolveExecutionFailureCommand(BaseCommand):
    command_type: Literal[CommandType.RESOLVE_EXECUTION_FAILURE] = (
        CommandType.RESOLVE_EXECUTION_FAILURE
    )
    failure_id: str = Field(min_length=1)
    decision: Literal["retry", "code_review"]


class ListRegistrySkillsCommand(BaseCommand):
    command_type: Literal[CommandType.LIST_REGISTRY_SKILLS] = CommandType.LIST_REGISTRY_SKILLS
    query: str | None = None


class CreateRegistrySkillCommand(BaseCommand):
    command_type: Literal[CommandType.CREATE_REGISTRY_SKILL] = CommandType.CREATE_REGISTRY_SKILL
    skill_id: str = Field(min_length=1)
    description: str = ""


class ShowCooReportCommand(BaseCommand):
    command_type: Literal[CommandType.SHOW_COO_REPORT] = CommandType.SHOW_COO_REPORT


class RouteManagerChatCommand(BaseCommand):
    command_type: Literal[CommandType.ROUTE_MANAGER_CHAT] = CommandType.ROUTE_MANAGER_CHAT
    text: str = Field(min_length=1)
    telegram_user_id: int


Command = (
    InitWorkspaceCommand
    | ListProjectsCommand
    | SwitchProjectCommand
    | CreateProjectCommand
    | CeoChatCommand
    | ShowGlobalConfigCommand
    | AddSkillToCompanyCommand
    | RemoveSkillFromCompanyCommand
    | UpdateGlobalConfigCommand
    | SetUserModeCommand
    | PmChatCommand
    | SetupWorkersCommand
    | AddWorkerCommand
    | AddSkillToProjectCommand
    | ShowProjectStatusCommand
    | ProjectGitCommand
    | ResolveApprovalCommand
    | PmRepairCommand
    | RunExecutionStepCommand
    | ResolveExecutionFailureCommand
    | ListRegistrySkillsCommand
    | CreateRegistrySkillCommand
    | ShowCooReportCommand
    | RouteManagerChatCommand
)
