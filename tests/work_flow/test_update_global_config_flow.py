import pytest

from ai_company.schemas.commands import UpdateGlobalConfigCommand


def test_update_global_config_command_requires_field():
    with pytest.raises(ValueError, match="至少需提供"):
        UpdateGlobalConfigCommand()


def test_dispatch_update_global_config_model(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import UpdateGlobalConfigCommand
    from ai_company.schemas.documents import NotificationPolicy

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    result = dispatch(
        UpdateGlobalConfigCommand(
            default_model="gemini-2.5-pro",
            max_output_tokens=2048,
            thinking_budget=0,
            notification_policy=NotificationPolicy.FAILURES_ONLY,
        ),
        deps,
    )
    assert result.success
    cfg = file_store.load_global_config(tmp_path)
    assert cfg.default_model == "gemini-2.5-pro"
    assert cfg.max_output_tokens == 2048
    assert cfg.notification_policy == NotificationPolicy.FAILURES_ONLY


def test_resolve_ai_generation_after_update(tmp_path):
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.settings import core as app_settings
    from ai_company.schemas.commands import UpdateGlobalConfigCommand
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    dispatch(UpdateGlobalConfigCommand(thinking_budget=0, max_output_tokens=1024), deps)
    gen = app_settings.resolve_ai_generation(file_store.load_global_config(tmp_path))
    assert gen.max_output_tokens == 1024
    assert gen.thinking_budget == 0
