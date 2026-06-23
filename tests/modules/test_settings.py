from ai_company.modules.settings.core import AppSettings, load_settings, resolve_ai_generation
from ai_company.schemas.documents import GlobalConfigFile


def test_resolved_gemini_api_key_google_takes_precedence(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    s = load_settings()
    assert s.resolved_gemini_api_key() == "google-key"


def test_resolved_gemini_api_key_falls_back_to_gemini(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "only-gemini")
    s = load_settings()
    assert s.resolved_gemini_api_key() == "only-gemini"


def test_resolve_ai_generation_defaults():
    gen = resolve_ai_generation(None)
    assert gen.max_output_tokens == 8192
    assert gen.thinking_budget == 0
    assert gen.include_thoughts is False


def test_global_config_file_ai_fields_defaults():
    gc = GlobalConfigFile()
    assert gc.max_output_tokens == 8192
    assert gc.thinking_budget == 0
