# 01 — 計畫、實作、驗證

## 適用

收到後端開發任務時使用本劇本。

## 步驟

1. **讀任務**：`pm/backend_current_task.yaml` 的 `goal` 與 `acceptance_criteria`；讀 `shared/requirements.md`（若 `context_refs` 有列出）。
2. **計畫**：用一兩句話列出要新增／修改的檔案（限 `workers/<你的 id>/` 與允許的 `shared/` 路徑）。
3. **實作**：用 `write_file` 寫程式與測試；測試檔建議放在 `workers/<id>/` 下。
4. **驗證**：用 `run_terminal` 執行 `python3 -m pytest` 指向你的測試路徑（或任務指定的測試指令）。若失敗，讀 stderr，修正後再跑，最多重試數輪由執行層限制。
5. **結束**：測試通過後呼叫 `complete_task`，`status=success`，並填寫 `test_command` 與 `test_exit_code=0`。

## 禁止

- 修改框架 `src/`、`_company/`、其他 worker 目錄。
- 自行 `pip install` 或任意 shell；缺依賴應在任務中說明或回報失敗。
