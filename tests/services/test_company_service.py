import pytest

from ai_company.services.company_service import CompanyService, format_projects_message
from ai_company.store.company_store import CompanyStore


def test_create_and_switch_project(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = CompanyService(tmp_workspace, store)
    p = svc.create_project("Alpha")
    svc.set_active_project(p.id)
    active = svc.get_active_project()
    assert active is not None
    assert active.name == "Alpha"


def test_switch_unknown_raises(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = CompanyService(tmp_workspace, store)
    with pytest.raises(ValueError, match="找不到專案"):
        svc.set_active_project("nope")


def test_bootstrap_default_from_migrated_tree(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    legacy = tmp_workspace / "projects" / "default" / "shared"
    legacy.mkdir(parents=True)
    svc = CompanyService(tmp_workspace, store)
    pf = svc.list_projects()
    assert any(p.id == "default" for p in pf.projects)
    assert pf.active_project_id == "default"


def test_format_projects_message_marks_active(tmp_workspace):
    store = CompanyStore(tmp_workspace)
    store.ensure_company_dirs()
    svc = CompanyService(tmp_workspace, store)
    a = svc.create_project("A")
    svc.create_project("B")
    svc.set_active_project(a.id)
    text = format_projects_message(svc.list_projects())
    assert f"{a.id} *" in text
