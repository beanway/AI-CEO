def test_pm_repair_interrupts_running_execution(tmp_path):
    from ai_company.adapters.dispatch import dispatch
    from ai_company.app_deps import AppDeps
    from ai_company.config import Settings
    from ai_company.modules.execution_store import core as execution_store
    from ai_company.modules.file_store import core as file_store
    from ai_company.schemas.commands import CreateProjectCommand, PmRepairCommand
    from ai_company.schemas.documents import ExecutionStateFile, ExecutionStatus
    from ai_company.schemas.workspace_paths import project_dir

    settings = Settings(company_workspace_root=tmp_path)
    deps = AppDeps(settings=settings)
    file_store.ensure_company_dirs(tmp_path)
    created = dispatch(CreateProjectCommand(name="RepairMe"), deps)
    execution_store.save_execution_state(
        tmp_path,
        ExecutionStateFile(
            execution_id="ex-1",
            project_id=created.project_id,
            worker_id="backend",
            status=ExecutionStatus.RUNNING,
        ),
    )

    inspect = dispatch(PmRepairCommand(project_id=created.project_id, interrupt=False), deps)
    assert inspect.success
    assert inspect.running_execution_count == 1

    interrupted = dispatch(
        PmRepairCommand(project_id=created.project_id, interrupt=True),
        deps,
    )
    assert interrupted.success
    assert interrupted.interrupted_execution_ids == ["ex-1"]
    state = execution_store.load_execution_state(tmp_path, "ex-1")
    assert state is not None
    assert state.status == ExecutionStatus.INTERRUPTED

    log_path = project_dir(tmp_path, created.project_id) / "pm" / "repair_log.jsonl"
    assert log_path.is_file()
