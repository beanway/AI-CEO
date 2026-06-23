# CEO 全公司預設（`company_workspace/_company/global_config.yaml`）

```yaml
default_model: gemini-2.5-flash
notification_policy: all
max_output_tokens: 8192
thinking_budget: 0
include_thoughts: false
# temperature: null   # 可選；省略表示不覆寫 SDK 預設
```

- `thinking_budget: 0`：關閉延伸 thinking 預算（與官網 `ThinkingConfig` 一致）
- 變更：CLI `update-global` 或手動編輯後，CEO 對話經 `settings.resolve_ai_generation` 生效
