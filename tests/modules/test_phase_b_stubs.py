def test_execution_dir(tmp_path):
    from ai_company.modules.execution_store.core import execution_dir

    assert execution_dir(tmp_path) == tmp_path / "_company" / "execution"


def test_save_and_interrupt_execution(tmp_path):
    from ai_company.modules.execution_store.core import (
        interrupt_execution,
        load_execution_state,
        save_execution_state,
    )
    from ai_company.schemas.documents import ExecutionStateFile, ExecutionStatus

    save_execution_state(
        tmp_path,
        ExecutionStateFile(execution_id="a1", project_id="p1"),
    )
    state = load_execution_state(tmp_path, "a1")
    assert state is not None
    assert state.status == ExecutionStatus.RUNNING
    interrupt_execution(tmp_path, "a1")
    assert load_execution_state(tmp_path, "a1").status == ExecutionStatus.INTERRUPTED
