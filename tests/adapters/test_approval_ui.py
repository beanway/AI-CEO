def test_parse_approval_callback():
    from ai_company.adapters.telegram.approval_ui import parse_approval_callback

    assert parse_approval_callback("approval:yes:abc1") == (True, "abc1")
    assert parse_approval_callback("approval:no:abc1") == (False, "abc1")
    assert parse_approval_callback("other:yes:abc1") is None
