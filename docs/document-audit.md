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
| `company_workspace/shared/` 等扁平目錄 | 存在 | 應在 `projects/<id>/` 下 | **是** |
| `src/ai_company/workspace.py` | `ensure_workspace` 建扁平五目錄 | 建 `_company/` + 專案子樹 | **是** |
| `src/ai_company/worker_state.py` | 固定 `WorkerState` 五角色 | 應讀 `workers.yaml` | **是**（Phase B 前可暫留） |
| `src/ai_company/router.py` | echo，無 CEO/PM | 管理者指令 + Session | **是**（未實作） |
| `.cursorrules` | 初版五原則 | 需反映 CEO/PM 範圍、動態 Worker | **部分** — 已建議更新 |
| 根 `README.md` | 指向舊 `SPEC.txt`、扁平沙盒 | 指向 `docs/README.md` | **已修正** |

---

## 4. 已刪除資產

| 檔案 | 說明 |
|------|------|
| `AI虛擬公司(...).docx` | 已刪；內容保留於 `reference/original-spec.txt` |

---

## 5. 建議下一步（非文件）

1. 依 Harness 重寫 `docs/plans/` 下 Phase A 實作計畫（舊檔僅作參考）。  
2. 實作 `migrate_flat_workspace` → `projects/default/`。  
3. 更新 `workspace.py` 與 Router，消除 §3 程式衝突。

---

## 6. 審查結論

- **文件集中於 `docs/` 後**：單一真相來源為 **`design/harness-design.md`**；無互斥的「現行」規格並存。  
- **殘留衝突**：主要在 **程式碼與 `company_workspace` 實體目錄** 仍為初版模型；**歸檔計畫** 與現設計 intentionally 不一致。  
- **歷史原文** `original-spec.txt` 僅作對照，不與 Harness 等同。
