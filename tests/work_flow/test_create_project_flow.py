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
    project_root = tmp_path / "projects" / result.project_id
    assert (project_root / ".git").is_dir()


def test_create_project_shell_rolls_back_on_session_failure(tmp_path, monkeypatch):
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.work_flow._shared.create_project_shell import create_project_shell

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)

    def boom(*_args, **_kwargs):
        raise OSError("simulated session write failure")

    monkeypatch.setattr(file_store, "init_pm_session", boom)

    try:
        create_project_shell(deps, "RollbackTest")
    except OSError:
        pass
    else:
        raise AssertionError("expected OSError")

    pf = file_store.load_projects(tmp_path)
    assert not any(p.name == "RollbackTest" for p in pf.projects)
    assert not list((tmp_path / "projects").glob("*/shared"))
