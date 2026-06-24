def test_dispatch_blocked_by_score_gate(tmp_path):
    import ai_company.work_flow._register  # noqa: F401
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.schemas.commands import RunExecutionStepCommand, UpdateGlobalConfigCommand
    from ai_company.schemas.documents import (
        ProjectHarnessStateFile,
        ProjectRecord,
        ProjectsFile,
        WorkerEntry,
        WorkersFile,
    )

    file_store.ensure_company_dirs(tmp_path)
    pid = "p1"
    pf = ProjectsFile(active_project_id=pid, projects=[ProjectRecord(id=pid, name="T")])
    file_store.save_projects(tmp_path, pf)
    root = project_folders.project_dir(tmp_path, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(
        workers=[
            WorkerEntry(id="scheduler", kind="task_scheduler"),
            WorkerEntry(id="qa", kind="qa"),
        ]
    )
    project_folders.ensure_worker_directories(root, workers.workers)
    file_store.save_workers(tmp_path, pid, workers)
    file_store.save_project_harness_state(
        tmp_path,
        pid,
        ProjectHarnessStateFile(last_completed_worker_id="scheduler"),
    )
    # scheduler 無 step marker → 低分
    cfg = file_store.load_global_config(tmp_path)
    file_store.save_global_config(
        tmp_path, cfg.model_copy(update={"dispatch_min_score": 80})
    )
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    step = dispatch(RunExecutionStepCommand(), deps)
    assert not step.success
    assert step.error_code == "score_below_threshold"

    dispatch(UpdateGlobalConfigCommand(dispatch_min_score=0), deps)
    ok = dispatch(RunExecutionStepCommand(), deps)
    assert ok.success
