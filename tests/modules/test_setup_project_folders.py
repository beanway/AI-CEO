from ai_company.modules.setup_project_folders.core import ensure_project_tree, project_dir


def test_project_tree_creates_shared_requirements(tmp_workspace):
    pdir = project_dir(tmp_workspace, "abc")
    ensure_project_tree(pdir)
    req = pdir / "shared" / "requirements.md"
    assert req.is_file()
    assert (pdir / "pm").is_dir()
