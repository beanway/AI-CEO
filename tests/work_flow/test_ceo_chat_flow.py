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


def test_ceo_session_tracks_active_project(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CeoChatCommand, CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path, gemini_api_key="")
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Ctx"), deps)
    assert created.success

    dispatch(CeoChatCommand(text="hi"), deps)
    record = file_store.load_ceo_session(tmp_path)
    assert record is not None
    assert record.project_id == created.project_id


def test_resolve_model_prefers_global_config(tmp_path):
    from ai_company.modules.settings import core as app_settings
    from ai_company.schemas.documents import GlobalConfigFile

    gc = GlobalConfigFile(default_model="gemini-2.0-flash")
    assert app_settings.resolve_model(gc) == "gemini-2.0-flash"


def test_resolve_ai_generation_from_global_config():
    from ai_company.modules.settings import core as app_settings
    from ai_company.schemas.documents import GlobalConfigFile

    gc = GlobalConfigFile(thinking_budget=0, max_output_tokens=4096)
    gen = app_settings.resolve_ai_generation(gc)
    assert gen.thinking_budget == 0
    assert gen.max_output_tokens == 4096
