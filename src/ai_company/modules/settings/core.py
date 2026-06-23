"""集中讀取 .env 與工作區設定檔，解析 AI／路徑等執行期設定。"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_company.schemas.ai_generation import AiGenerationSettings
from ai_company.schemas.documents import GlobalConfigFile

DEFAULT_MODEL = "gemini-2.5-flash"


class AppSettings(BaseSettings):
    """程序級設定（.env / 環境變數）。官網：GOOGLE_API_KEY 優先於 GEMINI_API_KEY。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_manager_bot_token: str = ""
    telegram_executor_bot_token: str = ""
    telegram_allowed_user_ids: str = ""

    gemini_api_key: str = ""
    google_api_key: str = ""

    company_workspace_root: Path | None = None

    @property
    def workspace_root(self) -> Path:
        if self.company_workspace_root:
            return self.company_workspace_root.expanduser().resolve()
        return (Path(__file__).resolve().parents[4] / "company_workspace").resolve()

    def resolved_gemini_api_key(self) -> str:
        if self.google_api_key.strip():
            return self.google_api_key.strip()
        return self.gemini_api_key.strip()

    def allowed_user_ids(self) -> set[int]:
        if not self.telegram_allowed_user_ids.strip():
            return set()
        return {int(x.strip()) for x in self.telegram_allowed_user_ids.split(",") if x.strip()}


def load_settings() -> AppSettings:
    return AppSettings()


def resolve_model(global_config: GlobalConfigFile | None = None) -> str:
    if global_config is not None and global_config.default_model.strip():
        return global_config.default_model.strip()
    return DEFAULT_MODEL


def resolve_ai_generation(global_config: GlobalConfigFile | None = None) -> AiGenerationSettings:
    if global_config is None:
        return AiGenerationSettings()
    return AiGenerationSettings(
        max_output_tokens=global_config.max_output_tokens,
        thinking_budget=global_config.thinking_budget,
        include_thoughts=global_config.include_thoughts,
        temperature=global_config.temperature,
    )
