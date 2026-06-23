"""Outbound results: work_flow → adapters / format_messages."""

from __future__ import annotations

from pydantic import BaseModel, Field, Field


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
    approval_id: str | None = None


class ShowProjectStatusResult(FlowResult):
    project_id: str | None = None


class ProjectGitResult(FlowResult):
    project_id: str | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    approval_id: str | None = None


class ResolveApprovalResult(FlowResult):
    approval_id: str | None = None
    approved: bool | None = None
    exit_code: int | None = None


class PmRepairResult(FlowResult):
    project_id: str | None = None
    running_execution_count: int | None = None
    interrupted_execution_ids: list[str] = Field(default_factory=list)
