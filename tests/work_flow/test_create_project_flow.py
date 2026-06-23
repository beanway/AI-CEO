def test_registry_includes_create_project_flow():
    from ai_company.work_flow.registry import registry
    from ai_company.work_flow import _register  # noqa: F401

    ids = {f.flow_id for f in registry.list_flows()}
    assert "create_project__work_flow" in ids


def test_dispatch_create_project(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    result = dispatch(CreateProjectCommand(name="Beta"), deps)
    assert result.success
    assert result.project_id
    pf = file_store.load_projects(tmp_path)
    assert any(p.id == result.project_id and p.name == "Beta" for p in pf.projects)
    session = tmp_path / "_company" / "sessions" / f"pm_{result.project_id}.json"
    assert session.is_file()
