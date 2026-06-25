def test_pm_resync_worker_overwrites_package(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.modules.worker_runner import core as worker_runner
    from ai_company.schemas.commands import CreateProjectCommand, PmResyncWorkerCommand
    from ai_company.schemas.documents import WorkerEntry, WorkersFile

    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="Sync"), deps)
    pid = created.project_id
    root = project_folders.project_dir(tmp_path, pid)
    workers = WorkersFile(workers=[WorkerEntry(id="backend", kind="backend")])
    file_store.save_workers(tmp_path, pid, workers)
    project_folders.ensure_worker_directories(root, workers.workers)
    worker_runner.copy_worker_default_into_worker_dir(root, "backend")
    pkg_file = root / "workers" / "backend" / "package" / "backend_worker" / "run.py"
    pkg_file.write_text("# tampered\n", encoding="utf-8")

    result = dispatch(
        PmResyncWorkerCommand(project_id=pid, template="backend", force_package=True),
        deps,
    )
    assert result.success
    text = pkg_file.read_text(encoding="utf-8")
    assert "run_scripted" in text
