# E-P 之後：未完成與過渡狀態

**日期**：2026-06-25  
**對照**：E-P0–E-P6 已完成（[`phase-e-worker-packages.md`](phase-e-worker-packages.md)）；規格 [`design/worker-sandbox-packages.md`](../design/worker-sandbox-packages.md)  
**用途**：給產品／實作排程；避免與「已交付的 E-P」混淆。

---

## 1. 使用者可感知落差（優先釐清）

| 現象 | 原因 | 目標狀態 |
|------|------|----------|
| 對 PM 交代任務後，scheduler **不會自動**開始規劃 | PM 對話**未**寫入 `pm/scheduler_intake.yaml` | PM 需求分析 → 產出 **intake** → scheduler 讀 intake |
| run-step 輪到 scheduler，但像「空跑一步」 | 專案**沒有** `pm/scheduler_intake.yaml` 時仍只寫 **harness 標記**（`.harness_step_done`），不跑完整 package 規劃 | 政策二選一：禁止派 scheduler／或建局時建立 intake |
| run-step 輪到 backend，有時只打勾 | 專案**沒有** `pm/backend_current_task.yaml` 時同樣只寫 harness 標記 | 派 backend 前須有任務契約，或 PM 從 intake 鏈寫入 |
| 改沙盒 `workers/backend/package/` **改不到**「真 AI 寫碼」 | **Gemini backend** 仍走 `worker_runner._run_backend_worker_gemini_impl`（框架內 agent 迴圈） | Gemini 迴圈遷入沙盒 package 或 package 可插拔 driver |
| `/resync`、`/loadfixture` 在 TG 可能沒有 | 已接 **`/resyncworker`**、**`/loadfixture`** 與 CLI `resync-worker`、`load-fixture-scenario` | — |

**Intake 語意**（產品）：交給任務分配者的開工輸入 = `pm/scheduler_intake.yaml`（`user_goal`、`context_refs`）。PM 口頭分析 ≠ intake，除非寫成該檔或等同 flow。

---

## 2. 架構／程式過渡（E-P 後仍留）

| 項目 | 現狀 | 建議下一步 |
|------|------|------------|
| `modules/worker_runner/` | scripted 已轉發 `worker_host`；**Gemini**、部分 **internal**（`scheduler_runner` 本體、`harness_tools`）仍在框架 | 刪除單體邏輯前：Gemini 遷移 + 架構測試 |
| `scheduler_runner.py` | `run_scheduler_worker_scripted` 已薄轉發；檔內 **agent 迴圈**等仍保留（未完全刪） | 確認無引用後刪除或僅留 re-export |
| `run_execution_step` 的 host 路徑 | `execution_step_entry` 為 **無 LLM  stub**（寫最小 `last_run.json` + 標記），非完整 AI 規劃／實作 | E3：真 LLM 在 package 或 host 注入 driver |
| `.harness_step_done` | run-step **仍會**在 host 成功後寫標記 | 終態以 `last_run.json` 為準，標記可移除（execution-layer-v2 §4.3） |
| `skills/registry/` E1 backend 共用 skill | roadmap §十六 步驟 **3–7 未完成** | §4.4 id 建立 + `role_skills.yaml` + Training 端到端 |

---

## 3. 產品能力（原 roadmap E3／E4，未做）

- **Scheduler v2**：使用者／PM 提問 → AI 分析 → 結構化任務列表 → 派工（非固定 pipeline 順序）。
- **PM 進階**：對話產 **intake**、寫 `shared/requirements.md`、觸發 scheduler；與 TG 核准整合。
- **執行期**自動 find/install skill（延後）。
- **Scheduler 主導** code review／打回（相對現有 `resolve_execution_failure` 人機關卡）。
- **結構化任務評分** 作為派工閘道（決策 B 第一版不做）。

---

## 4. PM 維修（已做 vs 未做）

| 已有 | 未有 |
|------|------|
| `/repair` 摘要、中斷 execution、**Worker 健檢清單**（manifest／package import） | 健檢後 **一鍵修復**（除 resync 種子外） |
| `pm_resync_worker__work_flow`（dispatch／測試／TG／CLI） | — |
| `load_fixture_scenario__work_flow`（dispatch／測試／TG／CLI） | — |
| resync **force_package** | resync 細粒度（只 skills、保留 package 自訂）文件化與 UX |

---

## 5. 測試與驗收缺口

- **Training 專案**（`d668c955`）手動端到端：roadmap §十六 步驟 7，未勾。
- **`test_backend_worker_live.py`**：依環境 API key，非 CI 必跑。
- **`scripts/simulate_p_a3_acceptance.py`**：repair 段落是否需更新納入 health 欄位（待確認）。

---

## 6. 建議實作順序（非強制）

1. **PM → intake flow**（對齊使用者心智：交代任務 = intake + 可選 requirements）。
2. **TG／CLI** 暴露 resync、load-fixture。
3. **run-step 政策**：backend／scheduler 無契約則 **failed** 或 **skip 並提示**，避免「假完成」。
4. **Gemini backend** 遷入 `backend_worker` package（PM 可改 prompt／工具編排）。
5. **E1 步驟 3–7**（registry skills、Gemini run-step 驗收、Training）。
6. **E3 scheduler v2**（LLM 規劃 + 移除固定 pipeline 依賴）。

---

## 7. 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-06-25 | E-P 完成後整理未完成與過渡狀態 |
