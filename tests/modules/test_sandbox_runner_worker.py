def test_complete_worker_step_in_sandbox(tmp_path):
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.modules.sandbox_runner.core import (
        complete_worker_harness_step,
        worker_sandbox_cwd,
    )
    from ai_company.schemas.documents import WorkerEntry, WorkersFile

    file_store.ensure_company_dirs(tmp_path)
    pid = "p1"
    root = project_folders.project_dir(tmp_path, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(workers=[WorkerEntry(id="be", kind="backend")])
    project_folders.ensure_worker_directories(root, workers.workers)
    assert worker_sandbox_cwd(tmp_path, pid, "be") == root.resolve()
    result = complete_worker_harness_step(tmp_path, pid, "be")
    marker = root / result.marker_path
    assert marker.is_file()
    assert result.marker_path == "workers/be/.harness_step_done"


def test_worker_cwd_outside_rejected(tmp_path):
    from ai_company.modules.sandbox_runner.core import ToolPolicyError, complete_worker_harness_step

    try:
        complete_worker_harness_step(tmp_path, "missing", "x")
    except ToolPolicyError:
        return
    raise AssertionError("expected ToolPolicyError")
