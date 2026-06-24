def test_enqueue_dequeue_queue(tmp_path):
    from ai_company.modules.execution_store import core as execution_store

    item = execution_store.enqueue_dispatch(
        tmp_path, project_id="p1", worker_id="backend"
    )
    assert item.project_id == "p1"
    assert item.worker_id == "backend"
    assert execution_store.peek_next_pending(tmp_path) is not None
    dequeued = execution_store.dequeue_next_pending(tmp_path)
    assert dequeued is not None
    assert dequeued.worker_id == "backend"
    assert execution_store.peek_next_pending(tmp_path) is None


def test_list_running_globally(tmp_path):
    from ai_company.modules.execution_store import core as execution_store
    from ai_company.schemas.documents import ExecutionStateFile, ExecutionStatus

    execution_store.save_execution_state(
        tmp_path,
        ExecutionStateFile(execution_id="e1", project_id="a", worker_id="planner"),
    )
    execution_store.save_execution_state(
        tmp_path,
        ExecutionStateFile(
            execution_id="e2",
            project_id="b",
            worker_id="qa",
            status=ExecutionStatus.DONE,
        ),
    )
    running = execution_store.list_running_globally(tmp_path)
    assert len(running) == 1
    assert running[0].execution_id == "e1"


def test_queue_persisted_on_disk(tmp_path):
    from ai_company.modules.execution_store import core as execution_store

    execution_store.enqueue_dispatch(tmp_path, project_id="x", worker_id="scheduler")
    reloaded = execution_store.load_queue_state(tmp_path)
    assert len(reloaded.pending) == 1
