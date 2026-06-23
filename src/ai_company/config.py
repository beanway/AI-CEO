"""相容層：請優先使用 modules.settings.core。"""

from ai_company.modules.settings.core import AppSettings, load_settings

Settings = AppSettings


def get_settings() -> AppSettings:
    return load_settings()
