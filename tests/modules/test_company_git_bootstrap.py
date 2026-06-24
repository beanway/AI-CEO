def test_bootstrap_company_local_git(tmp_path):
    from ai_company.config import Settings
    from ai_company.modules.company_git_bootstrap import core as company_git
    from ai_company.modules.file_store import core as file_store

    file_store.ensure_company_dirs(tmp_path)
    file_store.ensure_company_index_files(tmp_path)

    settings = Settings(company_workspace_root=tmp_path, github_owner="")
    msg = company_git.bootstrap_company_github(
        tmp_path,
        settings,
        create_remote=False,
    )
    root = tmp_path / "_company"
    assert (root / ".git").is_dir()
    assert "sessions/" in (root / ".gitignore").read_text(encoding="utf-8")
    assert "失敗" not in msg
