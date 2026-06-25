# 文件與程式碼一致性審查

**日期**：2026-06-22  
**Canonical 設計**：[`design/harness-design.md`](design/harness-design.md)

---

## 1. 文件之間

| 檔案 A | 檔案 B | 關係 | 衝突？ |
|--------|--------|------|--------|
| `harness-design.md` | `framework-design-v1-archived.md` | 後者已廢止 | 否（已標 archived） |
| `harness-design.md` | `phase-a-management-v1-archived.md` | 計畫依初版 spec | **是（預期）** — 計畫勿再執行，需重寫 |
| `harness-design.md` | `reference/original-spec.txt` | 歷史原文 | **部分** — 見 §2 |
| `harness-design.md` | `discussion-outcomes.md` | 摘要一致 | 否 |
| `harness-design.md` | `roadmap.md` | 路線對齊 Harness | 否 |
| `harness-design.md` | `execution-layer-v2.md` | §7.4 指向 v2 細節 | 否 |
| `harness-design.md` | `worker-sandbox-packages.md` | §5.5 三 package | 否 |
| `execution-layer-v2.md` | `worker_runner`／`worker_host` | Gemini 仍在 runner；無 intake／任務契約時 run-step 仍可能只標記 | **預期過渡**（見 [`plans/phase-e-worker-backlog.md`](plans/phase-e-worker-backlog.md)） |
| `worker-sandbox-packages.md` | 產品行為 | E-P 骨架完成；PM→intake、TG 指令等見 backlog | **追蹤中** |
| `src-layout.md` | `harness-design.md` | 程式分層實作產品設計 | 否 |
| `harness-design.md` | 根目錄 `README.md` | 應指向 `docs/` | **已修正**（見下方程式碼表） |

---

## 2. Harness 設計 vs 原始規格（`reference/original-spec.txt`）

| 主題 | 原文 | Harness／討論後 | 處理 |
|------|------|-----------------|------|
| 沙盒目錄 | 公司級 `shared/` + 固定四 Worker 目錄 | `projects/<id>/` + 動態 `workers/` | **以 Harness 為準** |
| 任務排程者 | 執行者 Bot 帳號 B 上之「橋樑」 | Bot B = 通知；**scheduler = 專案 Worker** | **以 Harness 為準** |
| CEO | 建專案 + 切換 | 建殼；全公司 global skill/config | **擴充** |
| PM | Git、對話 | 建局、編制、維修、狀態、Git | **擴充** |
| COO | 管理層角色 | 第二期 | **延後**（一致於討論） |
| 管理層併發 Session | CEO/PM/COO | CEO+PM MVP；COO 二期 | **部分延後** |
| 狀態機單 Worker | 是 | 是 | 一致 |
| 不遙控 Cursor | 未寫明 | 明確禁止 | **討論補充** |

---

## 3. 程式碼／設定 vs Harness 設計

| 位置 | 現狀 | 設計期望 | 衝突 |
|------|------|----------|------|
| `company_workspace/shared/` 等扁平目錄 | 可能仍存在 | 遷移至 `projects/<id>/`（`setup_workspace`） | **部分** |
| `modules/setup_workspace` | 已實作 | Harness 工作區根 | **已對齊** |
| `src/ai_company/worker_state.py` | 固定 `WorkerState` 五角色 | 應讀 `workers.yaml` | **是**（Phase B 前可暫留） |
| `src/ai_company/router.py` | 管理者指令經 dispatch | Session、完整 CEO/PM | **部分**（Phase A1） |
| `src/ai_company/work_flow/` | `run.py` + modules | 全產品 flow | **進行中** |
| `services/`、`store/` | 已刪除 | — | **已解決** |
| `modules/file_store` 等 | 已建立 | A1 | **已對齊** |
| `modules/settings` | 已建立 | .env + global_config 解析 | **已對齊** |
| `.cursor/rules`、`ai-ceo-framework` skill | 已對齊 src-layout | — | **已更新** |

---

## 4. 已刪除資產

| 檔案 | 說明 |
|------|------|
| `AI虛擬公司(...).docx` | 已刪；內容保留於 `reference/original-spec.txt` |

---

## 5. 建議下一步（非文件）

1. 執行 [`plans/phase-a-src-layout.md`](plans/phase-a-src-layout.md) A1 模組遷移。  
2. 新增 flow 時只改 `work_flow/_register.py` 與 adapters 路由表。  
3. Phase B 接上 `modules/ai_core`、`execution_store`。

---

## 6. 審查結論

- **文件集中於 `docs/` 後**：單一真相來源為 **`design/harness-design.md`**；無互斥的「現行」規格並存。  
- **殘留衝突**：`company_workspace` 扁平目錄遷移、`worker_state` 與動態 `workers.yaml`（Phase B）；框架分層 A1 已完成。  
- **歷史原文** `original-spec.txt` 僅作對照，不與 Harness 等同。
