from pathlib import Path

from ai_company.modules.setup_workspace.internal import migrate_repo_root
from ai_company.schemas.documents import ProjectsFile
from ai_company.schemas.workspace_paths import resolve_company_workspace_root


def test_resolve_company_workspace_root_relative_to_repo():
    root = resolve_company_workspace_root(Path("company_workspace"))
    assert root.name == "company_workspace"
    assert (root.parent / "src").is_dir()


def test_resolve_company_workspace_root_default():
    root = resolve_company_workspace_root(None)
    assert root.name == "company_workspace"


def test_migrate_repo_root_projects_and_company(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()

    workspace = repo / "company_workspace"
    workspace.mkdir()
    (workspace / "_company").mkdir()
    (workspace / "_company" / "projects.json").write_text(
        '{"active_project_id": null, "projects": []}',
        encoding="utf-8",
    )

    legacy_proj = repo / "projects" / "abc12345"
    legacy_proj.mkdir(parents=True)
    (legacy_proj / "shared").mkdir()

    legacy_company = repo / "_company"
    legacy_company.mkdir()
    pf = ProjectsFile(
        active_project_id="abc12345",
        projects=[],
    )
    from ai_company.schemas.documents import ProjectRecord

    pf.projects.append(ProjectRecord(id="abc12345", name="X"))
    (legacy_company / "projects.json").write_text(
        pf.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (legacy_company / "sessions").mkdir()
    (legacy_company / "sessions" / "pm_abc12345.json").write_text("{}", encoding="utf-8")

    moved = migrate_repo_root.migrate_repo_root_company_layout(repo, workspace)
    assert any("abc12345" in m for m in moved)
    assert (workspace / "projects" / "abc12345" / "shared").is_dir()
    merged = ProjectsFile.model_validate_json(
        (workspace / "_company" / "projects.json").read_text(encoding="utf-8")
    )
    assert merged.active_project_id == "abc12345"
    assert (workspace / "_company" / "sessions" / "pm_abc12345.json").is_file()
    assert not (repo / "projects" / "abc12345").exists()
