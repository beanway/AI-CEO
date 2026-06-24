"""Web 通道：JSON Command → dispatch。"""

from __future__ import annotations

import json
from typing import Any

from pydantic import TypeAdapter, ValidationError

from ai_company.adapters.deps import AppDeps
from ai_company.adapters.dispatch import dispatch
from ai_company.schemas.commands import Channel, Command

_command_adapter = TypeAdapter(Command)


def parse_command_body(body: dict[str, Any]) -> Command:
    data = dict(body)
    if "channel" not in data:
        data["channel"] = Channel.WEB.value
    return _command_adapter.validate_python(data)


def dispatch_json(body: dict[str, Any], deps: AppDeps) -> dict[str, Any]:
    try:
        command = parse_command_body(body)
    except ValidationError as exc:
        return {
            "success": False,
            "message": str(exc),
            "error_code": "invalid_command",
        }
    result = dispatch(command, deps)
    return json.loads(result.model_dump_json())
