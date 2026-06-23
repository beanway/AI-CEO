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
| `ceo_cli.py` | 本機 CEO CLI（`run.sh`） |
| `router.py` | 雙 Telegram Bot |

## 過渡期

`services/`、`store/`、`models/` 仍可能存在；新程式請依 src-layout 放入 `modules/` 與 `work_flow/`。
