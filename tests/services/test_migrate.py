from ai_company.services.migrate import migrate_flat_workspace


def test_migrate_moves_shared(tmp_workspace):
    flat_shared = tmp_workspace / "shared"
    flat_shared.mkdir()
    (flat_shared / "requirements.md").write_text("legacy", encoding="utf-8")
    pid = migrate_flat_workspace(tmp_workspace)
    assert pid == "default"
    dest = tmp_workspace / "projects" / "default" / "shared" / "requirements.md"
    assert dest.read_text(encoding="utf-8") == "legacy"
    assert not flat_shared.exists()
