def test_execution_dir(tmp_path):
    from ai_company.modules.execution_store.core import execution_dir

    assert execution_dir(tmp_path) == tmp_path / "_company" / "execution"
