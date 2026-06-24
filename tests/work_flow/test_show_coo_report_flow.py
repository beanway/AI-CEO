def test_show_coo_report_after_chat(tmp_path):
    import ai_company.work_flow._register  # noqa: F401
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CeoChatCommand, ShowCooReportCommand

    file_store.ensure_company_dirs(tmp_path)
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    chat = dispatch(CeoChatCommand(text="hello"), deps)
    assert chat.success
    report = dispatch(ShowCooReportCommand(), deps)
    assert report.success
    assert report.total_events is not None and report.total_events >= 1
