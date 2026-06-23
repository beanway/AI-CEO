import subprocess

def test_validate_git_rejects_path_outside_sandbox(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand, ProjectGitCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="GitTest"), deps)
    outside = tmp_path / "outside"
    outside.mkdir()
    result = dispatch(
        ProjectGitCommand(
            git_argv=["-C", str(outside), "status"],
            project_id=created.project_id,
        ),
        deps,
    )
    assert not result.success
    assert result.error_code == "tool_policy"


def test_run_git_status_in_project(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand, ProjectGitCommand
    from ai_company.schemas.workspace_paths import project_dir

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="GitTest"), deps)
    assert created.success
    root = project_dir(tmp_path, created.project_id)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    result = dispatch(
        ProjectGitCommand(git_argv=["status"], project_id=created.project_id),
        deps,
    )
    assert result.success
    assert result.exit_code == 0
