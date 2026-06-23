# ai_company 套件

AI Harness 框架程式（**非** `company_workspace` 沙盒產物）。

## 閱讀順序

1. [`docs/design/src-layout.md`](../../docs/design/src-layout.md) — 目錄與依賴規則  
2. [`work_flow/README.md`](work_flow/README.md) — 已註冊流程  
3. [`modules/README.md`](modules/README.md) — 工具模組  
4. [`adapters/README.md`](adapters/README.md) — 通道路由表  

## 入口

| 檔案 | 說明 |
|------|------|
| `main.py` | `run` / `init-workspace` |
| `ceo_cli.py` | 轉發至 `python -m ai_company.adapters.cli` |
| `router.py` | 雙 Telegram Bot |

持久化模型過渡：`models/company.py`（逐步由 `schemas/documents.py` 對外宣告契約）。
