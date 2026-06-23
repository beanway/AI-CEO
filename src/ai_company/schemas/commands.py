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
    UPDATE_GLOBAL_CONFIG = "update_global_config"
    SET_USER_MODE = "set_user_mode"
    PM_CHAT = "pm_chat"
    SETUP_WORKERS = "setup_workers"
    ADD_SKILL_TO_PROJECT = "add_skill_to_project"
    SHOW_PROJECT_STATUS = "show_project_status"


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


class UpdateGlobalConfigCommand(BaseCommand):
    command_type: Literal[CommandType.UPDATE_GLOBAL_CONFIG] = CommandType.UPDATE_GLOBAL_CONFIG
    default_model: str | None = None
    notification_policy: NotificationPolicy | None = None
    max_output_tokens: int | None = Field(default=None, ge=1)
    thinking_budget: int | None = None
    include_thoughts: bool | None = None
    temperature: float | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> UpdateGlobalConfigCommand:
        if self.default_model is None and self.notification_policy is None:
            if self.max_output_tokens is None and self.thinking_budget is None:
                if self.include_thoughts is None and self.temperature is None:
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


class AddSkillToProjectCommand(BaseCommand):
    command_type: Literal[CommandType.ADD_SKILL_TO_PROJECT] = CommandType.ADD_SKILL_TO_PROJECT
    skill_id: str = Field(min_length=1)
    project_id: str | None = None


class ShowProjectStatusCommand(BaseCommand):
    command_type: Literal[CommandType.SHOW_PROJECT_STATUS] = CommandType.SHOW_PROJECT_STATUS
    project_id: str | None = None


Command = (
    InitWorkspaceCommand
    | ListProjectsCommand
    | SwitchProjectCommand
    | CreateProjectCommand
    | CeoChatCommand
    | ShowGlobalConfigCommand
    | AddSkillToCompanyCommand
    | UpdateGlobalConfigCommand
    | SetUserModeCommand
    | PmChatCommand
    | SetupWorkersCommand
    | AddSkillToProjectCommand
    | ShowProjectStatusCommand
)
