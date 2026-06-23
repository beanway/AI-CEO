import pytest

from ai_company.modules.ai_core import core as ai_core


@pytest.fixture(autouse=True)
def _reset_ai_backends():
    ai_core.reset_chat_backends_for_tests()
    yield
    ai_core.reset_chat_backends_for_tests()


def test_dispatch_ceo_chat_fake(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CeoChatCommand

    settings = Settings(company_workspace_root=tmp_path, gemini_api_key="")
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    r1 = dispatch(CeoChatCommand(text="你好"), deps)
    assert r1.success
    assert r1.reply
    assert "你好" in r1.reply

    session = tmp_path / "_company" / "sessions" / "ceo.json"
    assert session.is_file()

    r2 = dispatch(CeoChatCommand(text="第二句"), deps)
    assert r2.success


def test_resolve_model_prefers_global_config(tmp_path):
    from ai_company.config import Settings
    from ai_company.schemas.documents import GlobalConfigFile

    settings = Settings(company_workspace_root=tmp_path)
    gc = GlobalConfigFile(default_model="gemini-2.0-flash")
    assert ai_core.resolve_model(settings, gc) == "gemini-2.0-flash"
