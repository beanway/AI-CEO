"""集中讀取 .env 與工作區設定檔，解析 AI／路徑等執行期設定。"""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_company.schemas.ai_generation import AiGenerationSettings
from ai_company.schemas.documents import GlobalConfigFile

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_OUTPUT_TOKENS = 8192
DEFAULT_THINKING_BUDGET = 0


def default_global_config() -> GlobalConfigFile:
    """新建或補齊 `global_config.yaml` 時使用的 CEO 預設。"""
    return GlobalConfigFile(
        default_model=DEFAULT_MODEL,
        max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
        thinking_budget=DEFAULT_THINKING_BUDGET,
        include_thoughts=False,
        temperature=None,
    )


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

    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
    )
    google_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "google_api_key"),
    )

    company_workspace_root: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("COMPANY_WORKSPACE_ROOT", "company_workspace_root"),
    )
    web_api_key: str = Field(default="", validation_alias=AliasChoices("WEB_API_KEY", "web_api_key"))

    @property
    def workspace_root(self) -> Path:
        if self.company_workspace_root:
            return self.company_workspace_root.expanduser().resolve()
        return (Path(__file__).resolve().parents[4] / "company_workspace").resolve()

    def resolved_gemini_api_key(self) -> str:
        """官網：GOOGLE_API_KEY 與 GEMINI_API_KEY 皆可；兩者皆有時 GOOGLE 優先。"""
        if self.google_api_key.strip():
            return self.google_api_key.strip()
        return self.gemini_api_key.strip()

    def resolved_gemini_api_key_source(self) -> str | None:
        """除錯用：回傳 'google' | 'gemini' | None（不暴露 key 內容）。"""
        if self.google_api_key.strip():
            return "google"
        if self.gemini_api_key.strip():
            return "gemini"
        return None

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
        return AiGenerationSettings(
            max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
            thinking_budget=DEFAULT_THINKING_BUDGET,
            include_thoughts=False,
        )
    return AiGenerationSettings(
        max_output_tokens=global_config.max_output_tokens,
        thinking_budget=global_config.thinking_budget,
        include_thoughts=global_config.include_thoughts,
        temperature=global_config.temperature,
    )
