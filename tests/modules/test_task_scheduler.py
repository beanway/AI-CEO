from ai_company.schemas.documents import ProjectHarnessStateFile, ProjectLifecycle, WorkersFile, WorkerEntry


def test_pipeline_order():
    from ai_company.modules.task_scheduler import core as sched

    workers = WorkersFile(
        workers=[
            WorkerEntry(id="qa", kind="qa"),
            WorkerEntry(id="scheduler", kind="task_scheduler"),
            WorkerEntry(id="be", kind="backend"),
        ]
    )
    assert sched.execution_pipeline(workers) == ["scheduler", "be", "qa"]


def test_pick_until_project_done():
    from ai_company.modules.task_scheduler import core as sched

    workers = WorkersFile(
        workers=[
            WorkerEntry(id="scheduler", kind="task_scheduler"),
            WorkerEntry(id="qa", kind="qa"),
        ]
    )
    harness = ProjectHarnessStateFile()
    w1, h1 = sched.pick_next_worker(workers, harness)
    assert w1 == "scheduler"
    w2, h2 = sched.pick_next_worker(workers, h1.model_copy(update={"last_completed_worker_id": "scheduler"}))
    assert w2 == "qa"
    w3, h3 = sched.pick_next_worker(workers, h2.model_copy(update={"last_completed_worker_id": "qa"}))
    assert w3 is None
    assert h3.lifecycle == ProjectLifecycle.PROJECT_DONE
