"""Inbound commands: adapters → work_flow (discriminated by command_type)."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ai_company.schemas.documents import NotificationPolicy


class CommandType(str, Enum):
    INIT_WORKSPACE = "init_workspace"
    LIST_PROJECTS = "list_projects"
    SWITCH_PROJECT = "switch_project"
    CREATE_PROJECT = "create_project"
    CEO_CHAT = "ceo_chat"
    SHOW_GLOBAL_CONFIG = "show_global_config"
    ADD_SKILL_TO_COMPANY = "add_skill_to_company"
    UPDATE_GLOBAL_CONFIG = "update_global_config"


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


Command = (
    InitWorkspaceCommand
    | ListProjectsCommand
    | SwitchProjectCommand
    | CreateProjectCommand
    | CeoChatCommand
    | ShowGlobalConfigCommand
    | AddSkillToCompanyCommand
    | UpdateGlobalConfigCommand
)
