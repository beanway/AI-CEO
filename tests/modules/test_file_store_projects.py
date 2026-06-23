import pytest

from ai_company.modules.file_store import core as file_store
from ai_company.modules.format_messages.core import format_projects_message


def test_create_and_switch_project(tmp_workspace):
    file_store.ensure_company_dirs(tmp_workspace)
    p = file_store.create_project(tmp_workspace, "Alpha")
    file_store.set_active_project(tmp_workspace, p.id)
    active = file_store.get_active_project(tmp_workspace)
    assert active is not None
    assert active.name == "Alpha"


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
    a = file_store.create_project(tmp_workspace, "A")
    file_store.create_project(tmp_workspace, "B")
    file_store.set_active_project(tmp_workspace, a.id)
    text = format_projects_message(file_store.load_projects(tmp_workspace))
    assert f"{a.id} *" in text
