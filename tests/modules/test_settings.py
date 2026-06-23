from ai_company.modules.settings.core import AppSettings, load_settings, resolve_ai_generation
from ai_company.schemas.documents import GlobalConfigFile


def _env_isolated(**kwargs: object) -> AppSettings:
    """測試用：不讀 .env，避免本機 GEMINI_API_KEY 干擾。"""
    return AppSettings(_env_file=None, **kwargs)


def test_resolved_gemini_api_key_google_takes_precedence():
    s = _env_isolated(gemini_api_key="gemini-key", google_api_key="google-key")
    assert s.resolved_gemini_api_key() == "google-key"
    assert s.resolved_gemini_api_key_source() == "google"


def test_resolved_gemini_api_key_falls_back_to_gemini():
    s = _env_isolated(gemini_api_key="only-gemini", google_api_key="")
    assert s.resolved_gemini_api_key() == "only-gemini"
    assert s.resolved_gemini_api_key_source() == "gemini"


def test_env_vars_google_precedence_over_gemini(monkeypatch):
    """與官網一致：環境變數綁定 GEMINI_API_KEY / GOOGLE_API_KEY。"""
    monkeypatch.setenv("GEMINI_API_KEY", "env-gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "env-google")
    s = AppSettings(_env_file=None)
    assert s.resolved_gemini_api_key() == "env-google"
    assert s.resolved_gemini_api_key_source() == "google"


def test_get_settings_compat_layer():
    s = _env_isolated(google_api_key="from-google", gemini_api_key="")
    from ai_company.config import get_settings

    assert isinstance(get_settings(), AppSettings)
    assert s.resolved_gemini_api_key() == "from-google"


def test_get_chat_backend_uses_google_api_key_only():
    from ai_company.modules.ai_core import core as ai_core
    from ai_company.modules.ai_core.core import FakeChatBackend, GeminiChatBackend

    ai_core.reset_chat_backends_for_tests()
    s = _env_isolated(google_api_key="google-only-key", gemini_api_key="")
    backend = ai_core.get_chat_backend(s)
    assert isinstance(backend, GeminiChatBackend)
    assert not isinstance(backend, FakeChatBackend)
    ai_core.reset_chat_backends_for_tests()


def test_get_chat_backend_fake_when_no_keys():
    from ai_company.modules.ai_core import core as ai_core
    from ai_company.modules.ai_core.core import FakeChatBackend

    ai_core.reset_chat_backends_for_tests()
    s = _env_isolated(google_api_key="", gemini_api_key="")
    assert s.resolved_gemini_api_key_source() is None
    backend = ai_core.get_chat_backend(s)
    assert isinstance(backend, FakeChatBackend)
    ai_core.reset_chat_backends_for_tests()


def test_resolve_ai_generation_defaults():
    gen = resolve_ai_generation(None)
    assert gen.max_output_tokens == 8192
    assert gen.thinking_budget == 0
    assert gen.include_thoughts is False


def test_default_global_config_matches_settings():
    from ai_company.modules.settings.core import (
        DEFAULT_MAX_OUTPUT_TOKENS,
        DEFAULT_THINKING_BUDGET,
        default_global_config,
    )

    gc = default_global_config()
    assert gc.max_output_tokens == DEFAULT_MAX_OUTPUT_TOKENS
    assert gc.thinking_budget == DEFAULT_THINKING_BUDGET
    assert gc.include_thoughts is False


def test_load_settings_reads_dotenv_without_crash():
    """煙霧：本機有 .env 時 load_settings 仍可呼叫。"""
    s = load_settings()
    assert hasattr(s, "resolved_gemini_api_key")
