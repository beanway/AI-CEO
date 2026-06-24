def test_append_and_summarize_usage(tmp_path):
    from ai_company.modules.metrics import core as metrics

    metrics.append_usage_event(tmp_path, event="ceo_chat", tokens_estimated=100)
    metrics.append_usage_event(
        tmp_path, event="task_score", project_id="p1", tokens_estimated=0
    )
    summary = metrics.summarize_usage(tmp_path)
    assert summary.total_events == 2
    assert summary.total_tokens_estimated == 100
    assert summary.by_event["ceo_chat"] == 1
