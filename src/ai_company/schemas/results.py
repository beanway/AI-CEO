"""Outbound results: work_flow → adapters / format_messages."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FlowResult(BaseModel):
    """Generic result for Phase A flows (text for TG/CLI)."""

    success: bool = True
    message: str = ""
    error_code: str | None = None


class ListProjectsResult(FlowResult):
    pass


class SwitchProjectResult(FlowResult):
    project_id: str | None = None


class CreateProjectResult(FlowResult):
    project_id: str | None = None


class CeoChatResult(FlowResult):
    reply: str | None = None


class ShowGlobalConfigResult(FlowResult):
    pass


class AddSkillToCompanyResult(FlowResult):
    skill_id: str | None = None


class UpdateGlobalConfigResult(FlowResult):
    pass


class SetUserModeResult(FlowResult):
    mode: str | None = None


class PmChatResult(FlowResult):
    reply: str | None = None


class SetupWorkersResult(FlowResult):
    project_id: str | None = None
    worker_count: int | None = None


class AddSkillToProjectResult(FlowResult):
    project_id: str | None = None
    skill_id: str | None = None


class ShowProjectStatusResult(FlowResult):
    project_id: str | None = None
