def _setup_project(tmp_path):
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.schemas.documents import ProjectRecord, ProjectsFile, WorkerEntry, WorkersFile

    file_store.ensure_company_dirs(tmp_path)
    pf = ProjectsFile(active_project_id="p1", projects=[ProjectRecord(id="p1", name="T")])
    file_store.save_projects(tmp_path, pf)
    root = project_folders.project_dir(tmp_path, "p1")
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(
        workers=[
            WorkerEntry(id="scheduler", kind="task_scheduler"),
            WorkerEntry(id="qa", kind="qa"),
        ]
    )
    project_folders.ensure_worker_directories(root, workers.workers)
    file_store.save_workers(tmp_path, "p1", workers)


def test_run_step_failure_and_retry(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.notify import core as notify
    from ai_company.schemas.commands import (
        ResolveExecutionFailureCommand,
        RunExecutionStepCommand,
    )

    _setup_project(tmp_path)
    messages: list[tuple[int, str]] = []
    notify.set_notify_sink(lambda cid, text: messages.append((cid, text)))
    cfg = file_store.load_global_config(tmp_path)
    file_store.save_global_config(
        tmp_path, cfg.model_copy(update={"executor_notify_chat_id": 99})
    )
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))

    fail = dispatch(
        RunExecutionStepCommand(simulate_failure=True),
        deps,
    )
    assert not fail.success
    assert fail.failure_id

    blocked = dispatch(RunExecutionStepCommand(), deps)
    assert blocked.error_code == "pending_failure"

    resolved = dispatch(
        ResolveExecutionFailureCommand(
            failure_id=fail.failure_id,
            decision="retry",
        ),
        deps,
    )
    assert resolved.success

    ok = dispatch(RunExecutionStepCommand(), deps)
    assert ok.success
    assert messages
    notify.set_notify_sink(None)


def test_run_step_backend_via_worker_host(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.worker_runner import core as worker_runner
    from ai_company.schemas.commands import RunExecutionStepCommand
    from ai_company.schemas.documents import ProjectRecord, ProjectsFile, WorkerEntry, WorkersFile
    from ai_company.modules.setup_project_folders import core as project_folders

    file_store.ensure_company_dirs(tmp_path)
    pf = ProjectsFile(active_project_id="pb", projects=[ProjectRecord(id="pb", name="B")])
    file_store.save_projects(tmp_path, pf)
    worker_runner.seed_backend_worker_project(tmp_path, "pb")
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    result = dispatch(RunExecutionStepCommand(project_id="pb"), deps)
    assert result.success, result.message
    last = worker_runner.load_last_run(tmp_path, "pb", "backend")
    assert last is not None and last.status == "success"


def test_full_pipeline_project_done(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import RunExecutionStepCommand
    from ai_company.schemas.documents import ProjectLifecycle

    _setup_project(tmp_path)
    deps = AppDeps(settings=Settings(company_workspace_root=tmp_path))
    for _ in range(3):
        result = dispatch(RunExecutionStepCommand(), deps)
        assert result.success, result.message
        if result.project_done:
            break
    harness = file_store.load_project_harness_state(tmp_path, "p1")
    assert harness.lifecycle == ProjectLifecycle.PROJECT_DONE
    pf = file_store.load_projects(tmp_path)
    rec = next(p for p in pf.projects if p.id == "p1")
    assert rec.status == "project_done"
    from ai_company.schemas.workspace_paths import project_dir

    assert (project_dir(tmp_path, "p1") / "shared" / "qa_passed.txt").is_file()
    log = project_dir(tmp_path, "p1") / "pm" / "scheduler_decisions.jsonl"
    assert log.is_file()
    assert "project_done" in log.read_text(encoding="utf-8")
