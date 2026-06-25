# Phase E-P — Worker 三 Package 分步實作

**規格**：[`design/worker-sandbox-packages.md`](../design/worker-sandbox-packages.md)  
**契約**：[`design/execution-layer-v2.md`](../design/execution-layer-v2.md) §4.2  
**原則**：每一步 **合併前** 須 `pytest` 全綠（或本步新增測試綠燈）；禁止跳步改架構。

---

## 步驟總覽

| 步驟 | 範圍 | 驗證（必做） |
|------|------|----------------|
| **E-P0** | 文件與決策（本計畫 + worker-sandbox-packages） | 人工對照 harness／execution-layer-v2 |
| **E-P1** | 種子目錄：`worker_manifest.yaml`、各 `package/` 骨架；擴充 copy／install | `tests/modules/test_worker_default_install.py`、`test_worker_package_layout.py`（新增） |
| **E-P2** | `modules/worker_host`：載入 manifest、import 沙盒 entrypoint；backend 走 host | `tests/modules/test_worker_host_backend.py`；既有 `test_worker_runner.py` 改為 host 或標記 xfail 過渡 |
| **E-P3** | scheduler 邏輯遷入 `worker_default/scheduler/package/`；host 依 kind 派發 | `test_worker_runner_scheduler.py` → host 版；`test_scheduler_worker_scripted.py` |
| **E-P4** | fixtures package：`load_demo_scenario` → `pm/`；與 backend／scheduler 無 cross-import | `tests/modules/test_fixtures_package.py`；架構測試禁止 fixtures→backend import |
| **E-P5** | PM：`pm_resync_worker__work_flow`、`pm_repair` 健檢擴充 | `tests/work_flow/test_pm_resync_worker_flow.py`、`test_pm_repair_flow.py` 擴充 |
| **E-P6** | `run_execution_step` 接 host（backend／scheduler） | `test_run_execution_step_flow.py` 擴充；可選 Training 手動 |

---

## E-P0 — 文件（本 commit）

**產出**：`worker-sandbox-packages.md`、本檔；更新 harness、execution-layer-v2、roadmap、worker_default README。

**驗證**

```bash
# 無程式變更；可選：確認文件連結
rg -l 'worker-sandbox-packages' docs/
```

---

## E-P1 — 種子 layout + 複製

**產出**

- `worker_default/backend/package/backend_worker/`（最小 `run.py` stub）
- `worker_default/scheduler/package/scheduler_worker/`（stub）
- `worker_default/fixtures/package/fixtures_loader/`（stub + 沿用現有 YAML）
- `worker_default/*/worker_manifest.yaml`
- `default_install.copy_worker_default_into_worker_dir` 複製 manifest + package

**單元測試**

- 複製後沙盒具 manifest、package 可 `import`（專案根 + worker 路徑政策內）
- 三 package 目錄 **無** 相互 Python import（靜態掃描或架構測試）

**驗證**

```bash
pytest tests/modules/test_worker_default_install.py tests/modules/test_worker_package_layout.py -q
```

---

## E-P2 — worker_host + backend

**產出**

- `modules/worker_host/core.py`：`load_manifest`、`run_worker_entrypoint(project_root, worker_id, task_path)`
- backend entrypoint 實作契約輸出 `last_run.json`
- `worker_runner` 改為薄轉發或標記 deprecated，測試遷移

**單元測試**

- scripted／fake agent 路徑與現 E1 行為等價（`last_run.json`、測試 exit code）
- `tests/architecture/test_module_encapsulation.py` 仍通過

**驗證**

```bash
pytest tests/modules/test_worker_host_backend.py tests/worker_tests/test_backend_worker_scripted.py -q
```

---

## E-P3 — scheduler package

**產出**

- 自 `worker_runner/internal/scheduler_runner.py` 遷移邏輯至 `scheduler/package/`（host 只調度）
- `scheduler_harness_tools` 保留在 host 或下沉（以測試為準）

**驗證**

```bash
pytest tests/modules/test_worker_runner_scheduler.py tests/worker_tests/test_scheduler_worker_scripted.py -q
```

---

## E-P4 — fixtures package

**產出**

- CLI 或 flow：`load-fixture-scenario <name>` 寫入 `pm/*_current_task.yaml` 等
- fixtures 僅依賴 YAML 與 host 提供的讀寫 API

**驗證**

```bash
pytest tests/modules/test_fixtures_package.py -q
```

---

## E-P5 — PM resync + repair

**產出**

- `pm_resync_worker__work_flow`：`template` + `worker_id` + 可選 `force_package`
- `pm_repair__work_flow`：缺檔／manifest／import 錯誤清單

**驗證**

```bash
pytest tests/work_flow/test_pm_resync_worker_flow.py tests/work_flow/test_pm_repair_flow.py -q
python scripts/simulate_p_a3_acceptance.py   # 若仍適用 repair 段落
```

---

## E-P6 — run-step 整合

**產出**

- `run_execution_step__work_flow`：`kind in (backend, task_scheduler)` → `worker_host`

**驗證**

```bash
pytest tests/work_flow/test_run_execution_step_flow.py tests/modules/test_worker_host_backend.py -q
# 全量
pytest -q
```

---

## 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-06-25 | 初版分步計畫（E-P0–E-P6） |
