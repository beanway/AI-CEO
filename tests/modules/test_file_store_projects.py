import pytest

from ai_company.app_deps import AppDeps
from ai_company.config import Settings
from ai_company.modules.file_store import core as file_store
from ai_company.modules.format_messages.core import format_projects_message
from ai_company.work_flow._shared.create_project_shell import create_project_shell


def _deps(tmp_workspace):
    return AppDeps(settings=Settings(company_workspace_root=tmp_workspace))


def test_create_and_switch_project(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    p, _git = create_project_shell(_deps(tmp_workspace), "Alpha")
    file_store.set_active_project(tmp_workspace, p.id)
    active = file_store.get_active_project(tmp_workspace)
    assert active is not None
    assert active.name == "Alpha"
    session = tmp_workspace / "_company" / "sessions" / f"pm_{p.id}.json"
    assert session.is_file()
    assert not (tmp_workspace / "projects" / p.id / "workers.yaml").exists()


def test_switch_unknown_raises(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    with pytest.raises(ValueError, match="找不到專案"):
        file_store.set_active_project(tmp_workspace, "nope")


def test_bootstrap_default_from_migrated_tree(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    legacy = tmp_workspace / "projects" / "default" / "shared"
    legacy.mkdir(parents=True)
    pf = file_store.load_projects(tmp_workspace)
    assert any(p.id == "default" for p in pf.projects)
    assert pf.active_project_id == "default"


def test_format_projects_message_marks_active(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    deps = _deps(tmp_workspace)
    a, _ = create_project_shell(deps, "A")
    create_project_shell(deps, "B")
    file_store.set_active_project(tmp_workspace, a.id)
    text = format_projects_message(file_store.load_projects(tmp_workspace))
    assert f"{a.id} *" in text
