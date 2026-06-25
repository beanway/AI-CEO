def test_add_worker_backend_from_default(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="AddW"), deps)
    assert created.success

    result = dispatch(AddWorkerCommand(template="backend"), deps)
    assert result.success
    assert result.worker_id == "backend"
    assert result.kind == "backend"

    workers = file_store.load_workers(tmp_path, created.project_id)
    assert len(workers.workers) == 1
    assert workers.workers[0].id == "backend"

    skill = (
        tmp_path
        / "projects"
        / created.project_id
        / "workers"
        / "backend"
        / "skills"
        / "01_plan_implement_test.md"
    )
    assert skill.is_file()


def test_add_worker_duplicate_fails(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Dup"), deps)
    dispatch(AddWorkerCommand(template="backend"), deps)
    again = dispatch(AddWorkerCommand(template="backend"), deps)
    assert not again.success
    assert again.error_code == "duplicate_worker"


def test_add_worker_unknown_template(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import AddWorkerCommand, CreateProjectCommand

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    dispatch(CreateProjectCommand(name="X"), deps)
    result = dispatch(AddWorkerCommand(template="frontend"), deps)
    assert not result.success
    assert result.error_code == "unknown_template"
