from pathlib import Path
from typing import Literal

import yaml

from ai_company.schemas.documents import (
    GlobalConfigFile,
    GlobalSkillsFile,
    ProjectsFile,
    SessionRecord,
    UserPrefsFile,
)

# 舊版 YAML 若缺下列鍵，載入後會回寫完整檔案
_GLOBAL_CONFIG_PERSISTED_KEYS = frozenset(
    {"max_output_tokens", "thinking_budget", "include_thoughts"}
)

COMPANY_DIR = "_company"
SESSIONS_DIR = "sessions"
PROJECTS_DIR = "projects"


class FileStore:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.company_dir = workspace_root / COMPANY_DIR

    def ensure_company_dirs(self) -> None:
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        (self.workspace_root / PROJECTS_DIR).mkdir(exist_ok=True)
        (self.company_dir / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
        (self.company_dir / "execution").mkdir(exist_ok=True)
        (self.company_dir / "metrics").mkdir(exist_ok=True)

    def ensure_company_index_files(self) -> None:
        projects_path = self.company_dir / "projects.json"
        if not projects_path.exists():
            self.save_projects(ProjectsFile())

        skills_path = self.company_dir / "global_skills.yaml"
        if not skills_path.exists():
            self.save_global_skills(GlobalSkillsFile())

        config_path = self.company_dir / "global_config.yaml"
        if not config_path.exists():
            from ai_company.modules.settings.core import default_global_config

            self.save_global_config(default_global_config())
        else:
            self._upgrade_global_config_yaml_if_needed()

    def _upgrade_global_config_yaml_if_needed(self) -> None:
        path = self.company_dir / "global_config.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raw = {}
        if _GLOBAL_CONFIG_PERSISTED_KEYS.issubset(raw.keys()):
            return
        data = GlobalConfigFile.model_validate(raw)
        self.save_global_config(data)

    def _atomic_write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def load_projects(self) -> ProjectsFile:
        path = self.company_dir / "projects.json"
        if not path.exists():
            return ProjectsFile()
        return ProjectsFile.model_validate_json(path.read_text(encoding="utf-8"))

    def save_projects(self, data: ProjectsFile) -> None:
        self._atomic_write(
            self.company_dir / "projects.json",
            data.model_dump_json(indent=2),
        )

    def load_global_skills(self) -> GlobalSkillsFile:
        path = self.company_dir / "global_skills.yaml"
        if not path.exists():
            return GlobalSkillsFile()
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if raw is None:
            return GlobalSkillsFile()
        return GlobalSkillsFile.model_validate(raw)

    def save_global_skills(self, data: GlobalSkillsFile) -> None:
        body = yaml.safe_dump(
            data.model_dump(mode="json"),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        self._atomic_write(self.company_dir / "global_skills.yaml", body)

    def load_global_config(self) -> GlobalConfigFile:
        path = self.company_dir / "global_config.yaml"
        if not path.exists():
            return GlobalConfigFile()
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if raw is None:
            return GlobalConfigFile()
        return GlobalConfigFile.model_validate(raw)

    def save_global_config(self, data: GlobalConfigFile) -> None:
        body = yaml.safe_dump(
            data.model_dump(mode="json"),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        self._atomic_write(self.company_dir / "global_config.yaml", body)

    def load_user_prefs(self) -> UserPrefsFile:
        path = self.company_dir / "user_prefs.json"
        if not path.exists():
            return UserPrefsFile()
        return UserPrefsFile.model_validate_json(path.read_text(encoding="utf-8"))

    def save_user_prefs(self, data: UserPrefsFile) -> None:
        self._atomic_write(
            self.company_dir / "user_prefs.json",
            data.model_dump_json(indent=2),
        )

    def session_path(self, key: Literal["ceo"] | str) -> Path:
        if key == "ceo":
            return self.company_dir / SESSIONS_DIR / "ceo.json"
        return self.company_dir / SESSIONS_DIR / f"pm_{key}.json"

    def load_session(self, path: Path) -> SessionRecord | None:
        if not path.exists():
            return None
        return SessionRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def save_session(self, path: Path, record: SessionRecord) -> None:
        self._atomic_write(path, record.model_dump_json(indent=2))

    def write_text_file(self, path: Path, text: str) -> None:
        self._atomic_write(path, text)
