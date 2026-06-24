def test_score_worker_with_marker(tmp_path):
    from ai_company.modules.file_store import core as file_store
    from ai_company.modules.setup_project_folders import core as project_folders
    from ai_company.modules.task_scoring import core as task_scoring
    from ai_company.schemas.documents import WorkerEntry, WorkersFile

    file_store.ensure_company_dirs(tmp_path)
    pid = "p1"
    root = project_folders.project_dir(tmp_path, pid)
    project_folders.ensure_project_tree(root)
    workers = WorkersFile(workers=[WorkerEntry(id="be", kind="backend")])
    project_folders.ensure_worker_directories(root, workers.workers)
    (root / "workers" / "be" / ".harness_step_done").write_text("ok", encoding="utf-8")
    score = task_scoring.score_worker_output(tmp_path, pid, "be")
    assert score.value >= 40
