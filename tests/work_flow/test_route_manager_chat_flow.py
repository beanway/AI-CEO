def test_route_manager_chat_pm_mode(tmp_path):
    import ai_company.work_flow._register  # noqa: F401
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.ai_core import core as ai_core
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import (
        CreateProjectCommand,
        RouteManagerChatCommand,
        SetUserModeCommand,
        SwitchProjectCommand,
    )
    from ai_company.schemas.documents import UserMode

    ai_core.reset_chat_backends_for_tests()
    file_store.ensure_company_dirs(tmp_path)
    deps = AppDeps(
        settings=Settings(company_workspace_root=tmp_path, gemini_api_key="", google_api_key="")
    )
    created = dispatch(CreateProjectCommand(name="R"), deps)
    dispatch(SwitchProjectCommand(project_id=created.project_id), deps)
    dispatch(SetUserModeCommand(telegram_user_id=42, mode=UserMode.PM), deps)
    result = dispatch(
        RouteManagerChatCommand(text="hi", telegram_user_id=42),
        deps,
    )
    assert result.success
    ai_core.reset_chat_backends_for_tests()
