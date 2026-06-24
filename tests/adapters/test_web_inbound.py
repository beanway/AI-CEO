def test_web_dispatch_list_projects(tmp_path):
    import ai_company.work_flow._register  # noqa: F401
    from ai_company.adapters.deps import AppDeps
    from ai_company.adapters.web.inbound import dispatch_json
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store

    file_store.ensure_company_dirs(tmp_path)
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    out = dispatch_json({"command_type": "list_projects"}, deps)
    assert out["success"] is True
    assert "Active:" in out["message"]
