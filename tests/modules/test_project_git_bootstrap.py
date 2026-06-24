import subprocess

from ai_company.modules.project_git_bootstrap import core as bootstrap

def test_slug_repo_name():
    assert bootstrap.slug_repo_name("My App", "a1b2c3d4") == "my-app-a1b2c3d4"


def test_bootstrap_local_git_init(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_AUTO_CREATE_REPO", raising=False)
    from ai_company.config import Settings

    settings = Settings(company_workspace_root=tmp_path, github_auto_create_repo=False)
    root = tmp_path / "projects" / "p1"
    root.mkdir(parents=True)
    (root / "shared").mkdir()

    note = bootstrap.bootstrap_project_git(
        root,
        project_id="p1",
        project_name="Demo",
        settings=settings,
    )
    assert (root / ".git").is_dir()
    assert (root / ".gitignore").is_file()
    assert "git init" in note


def test_bootstrap_skips_gh_when_disabled(tmp_path):
    from ai_company.config import Settings

    settings = Settings(
        company_workspace_root=tmp_path,
        github_auto_create_repo=False,
        github_owner="acme",
    )
    root = tmp_path / "projects" / "x"
    root.mkdir(parents=True)

    note = bootstrap.bootstrap_project_git(
        root,
        project_id="x",
        project_name="X",
        settings=settings,
    )
    assert "GitHub" not in note
