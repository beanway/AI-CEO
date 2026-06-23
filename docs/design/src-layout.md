# 原始碼目錄結構（Canonical）

**日期**：2026-06-22  
**狀態**：已核准（與 Harness 產品設計並存；產品行為仍以 [`harness-design.md`](harness-design.md) 為準）  
**適用**：`src/ai_company/` 內 **框架程式**（非 `company_workspace` 沙盒產物）

---

## 1. 分層總覽

| 層 | 目錄 | 職責 |
|----|------|------|
| 通道 | `adapters/` | Telegram、CLI、（二期）Web：解析輸入 → `schemas.commands`；呼叫 `work_flow.registry`；送出回覆 |
| 流程 | `work_flow/` | 產品功能編排（含錯誤、回滾）；**唯一**可 `import modules.*.core` |
| 工具模組 | `modules/` | 可重用能力，**不含流程**；對外僅 `core.py` + `README.md` |
| 契約 | `schemas/` | Command / Result / Document DTO（對齊 JSON/YAML 與跨通道資料） |
| 程序 | `main.py`、`router.py`、`config.py`、`app_deps.py` | 啟動、雙 Bot 生命週期、設定、`AppDeps` 注入 |

**依賴規則**

- `adapters/*` → `schemas`、`work_flow`、`config`（不直接 import `modules`）
- `work_flow/**` → `modules/*/core`、`schemas`、`work_flow/_shared`
- `modules/**` → 同模組 `internal/`、`schemas`；**不得** import 其他模組的 `core`
- 改磁碟 JSON/YAML 欄位：先改 `schemas/documents.py` 與模組 README，再改單一 writer 模組

---

## 2. `work_flow/` 與統一註冊

- 每個功能一個目錄：`<slug>__work_flow/`（目錄名英文；中文說明寫在該目錄 `README.md`）。
- **公開實作僅 `run.py`**：`run(command, deps) -> Result` 與 `register(registry)`；`__init__.py` 空白。
- **註冊**：`work_flow/registry.py` 的 `WorkFlowRegistry`；`work_flow/_register.py` 匯入各 flow 的 `run.register`。
- 通道透過 `adapters/dispatch.py` 的 `dispatch(command, deps)`，不直呼單一 flow 路徑。
- 跨 flow 重複編排放在 `work_flow/_shared/`（非模組）。

索引表見 [`work_flow/README.md`](../../src/ai_company/work_flow/README.md)（與程式內 `registry.list_flows()` 對齊）。

---

## 3. `modules/` 工具模組（命名與用途）

| 目錄 | 中文（README 第一行） | 做什麼 |
|------|----------------------|--------|
| `file_store` | 設定檔讀寫 | 讀寫 `company_workspace` 內 JSON/YAML（projects、global、user_prefs、sessions…） |
| `setup_workspace` | 工作區根目錄建立 | 建立根目錄、`_company` 骨架、舊扁平目錄遷移 |
| `setup_project_folders` | 專案資料夾建立 | 針對 `projects/<id>/` 建立與解析標準資料夾樹 |
| `format_messages` | 回覆排版 | Result/DTO → 文字（或未來 TG 結構 dict） |
| `ai_core` | AI 供應商與對話 | Provider、模型解析、chat（Phase B+） |
| `execution_store` | 執行狀態持久化 | `execution/*.json`、狀態機資料（Phase B） |
| `sandbox_runner` | 沙盒指令執行 | ToolPolicy、cwd 限制、subprocess（Phase B） |
| `notify` | 出站通知 | 執行者 Bot 等（Phase B） |

**遷移狀態**：Phase A 重構進行中；過渡期仍可能存在 `services/`、`store/`、`models/`，新程式應依上表放入 `modules/`，並在 [`document-audit.md`](../document-audit.md) 追蹤刪除舊路徑。

---

## 4. 目錄樹（目標）

```text
src/ai_company/
├── README.md
├── config.py
├── app_deps.py
├── main.py
├── router.py
├── schemas/
│   ├── README.md
│   ├── commands.py
│   ├── results.py
│   └── documents.py
├── adapters/
│   ├── README.md
│   ├── deps.py
│   ├── dispatch.py
│   ├── telegram/
│   └── cli/
├── work_flow/
│   ├── README.md
│   ├── registry.py
│   ├── _register.py
│   ├── _shared/
│   └── <slug>__work_flow/
│       ├── README.md
│       ├── __init__.py          # 空白
│       └── run.py               # run() + register()
└── modules/
    ├── README.md
    └── <module_name>/
        ├── README.md
        ├── core.py
        └── internal/
```

---

## 5. 與 Harness 的關係

- **CEO / PM 邊界**：體現在「哪條 `*__work_flow` 被註冊、誰有權 dispatch」，不是模組資料夾名稱。
- **沙盒路徑**：`setup_project_folders` + `file_store` 協同；flow 負責編排與回滾。
- **Worker / 狀態機**：Phase B 新增 `execution_store`、`sandbox_runner` 等 flow，不恢復扁平五目錄。

---

## 6. 相關文件

- 產品與治理：[`harness-design.md`](harness-design.md)
- 實作階段：[`../roadmap.md`](../roadmap.md)
- 重構計畫：[`../plans/phase-a-src-layout.md`](../plans/phase-a-src-layout.md)
- Cursor 開發規範：`.cursor/skills/ai-ceo-framework/SKILL.md`、`.cursor/rules/python-harness.mdc`
