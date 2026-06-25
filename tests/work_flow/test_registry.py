def test_registry_lists_phase_a_flows():
    from ai_company.work_flow.registry import registry
    from ai_company.work_flow import _register  # noqa: F401

    flows = registry.list_flows()
    ids = {f.flow_id for f in flows}
    assert "list_projects__work_flow" in ids
    assert "switch_project__work_flow" in ids
    assert "create_project__work_flow" in ids
    assert "ceo_chat__work_flow" in ids
    assert "add_skill_to_company__work_flow" in ids
    assert "remove_skill_from_company__work_flow" in ids
    assert "update_global_config__work_flow" in ids
    assert "set_user_mode__work_flow" in ids
    assert "pm_chat__work_flow" in ids
    assert "pm_repair__work_flow" in ids
    assert "setup_workers__work_flow" in ids
    assert "add_worker__work_flow" in ids
    assert "project_git__work_flow" in ids
    assert len(flows) >= 24


def test_dispatch_list_projects(tmp_path):
    from ai_company.app_deps import AppDeps
    from ai_company.adapters.dispatch import dispatch
    from ai_company.config import Settings
    from ai_company.schemas.commands import ListProjectsCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    result = dispatch(ListProjectsCommand(), deps)
    assert result.success
    assert "Active:" in result.message
