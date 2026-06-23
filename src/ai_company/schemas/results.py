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


class ShowGlobalConfigResult(FlowResult):
    pass
