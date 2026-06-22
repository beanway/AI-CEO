from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_manager_bot_token: str = ""
    telegram_executor_bot_token: str = ""
    telegram_allowed_user_ids: str = ""

    gemini_api_key: str = ""

    company_workspace_root: Path | None = None

    @property
    def workspace_root(self) -> Path:
        if self.company_workspace_root:
            return self.company_workspace_root.expanduser().resolve()
        return (Path(__file__).resolve().parents[2] / "company_workspace").resolve()

    def allowed_user_ids(self) -> set[int]:
        if not self.telegram_allowed_user_ids.strip():
            return set()
        return {int(x.strip()) for x in self.telegram_allowed_user_ids.split(",") if x.strip()}


def get_settings() -> Settings:
    return Settings()
