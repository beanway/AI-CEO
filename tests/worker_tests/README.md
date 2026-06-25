# worker_tests — backend Worker 整合驗證

本目錄在單元測試（`tests/modules/test_worker_runner.py`）通過後，用 **真實 Gemini** 跑完整任務。

## 執行

```bash
# 離線（必過）：產物寫入 _sandbox/
python3 -m pytest tests/worker_tests/test_backend_worker_scripted.py -v

# 真實 Gemini（需 .env 內 GOOGLE_API_KEY 或 GEMINI_API_KEY）
python3 -m pytest tests/worker_tests/test_backend_worker_live.py -v
```

**種子副本**：[`backend_seed/`](backend_seed/)（自 `worker_default/backend/` 複製，對照用）

## 產物

執行後工作區在 `tests/worker_tests/_sandbox/company_workspace/`（gitignore），可查看：

- `projects/worker_live_test/workers/backend/calc.py`
- `projects/worker_live_test/workers/backend/last_run.json`

## 種子來源

與 `worker_default/` 相同；任務契約為 `worker_default/fixtures/backend_demo_task.yaml`。
