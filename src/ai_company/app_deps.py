from dataclasses import dataclass
from pathlib import Path

from ai_company.config import Settings


@dataclass(frozen=True)
class AppDeps:
    """Injected into work_flow.run(command, deps) and adapter dispatch."""

    settings: Settings

    @property
    def workspace_root(self) -> Path:
        return self.settings.workspace_root
