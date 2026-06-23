"""Inbound commands: adapters → work_flow (discriminated by command_type)."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    INIT_WORKSPACE = "init_workspace"
    LIST_PROJECTS = "list_projects"
    SWITCH_PROJECT = "switch_project"
    CREATE_PROJECT = "create_project"
    CEO_CHAT = "ceo_chat"
    SHOW_GLOBAL_CONFIG = "show_global_config"


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


Command = (
    InitWorkspaceCommand
    | ListProjectsCommand
    | SwitchProjectCommand
    | CreateProjectCommand
    | CeoChatCommand
    | ShowGlobalConfigCommand
)
