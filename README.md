# AI 虛擬公司 (AI Company Framework)

Python + Gemini + 雙 Telegram Bot 的 **AI Harness（駕馭層）** 虛擬軟體公司。

**文件（請由此進入）：** [`docs/README.md`](docs/README.md)  
**產品設計：** [`docs/design/harness-design.md`](docs/design/harness-design.md)  
**程式分層：** [`docs/design/src-layout.md`](docs/design/src-layout.md)

## 快速開始

```bash
cd /Users/yangpinwei/Documents/AI/git/AI-CEO
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# 編輯 .env：填入兩組 Bot Token（@BotFather）與 GEMINI_API_KEY

python -m ai_company.main init-workspace
python -m ai_company.main run

# 或使用互動選單（本機 CEO CLI + 啟動 Bot）
./run.sh
```

業務指令經 **`work_flow` 統一註冊**（`adapters.dispatch`）；見 [`src/ai_company/work_flow/README.md`](src/ai_company/work_flow/README.md)。

## 目錄

| 路徑 | 說明 |
|------|------|
| `docs/` | 產品／設計／路線圖／src-layout |
| `worker_default/` | E1 預設 Worker 種子（先於專案沙盒測試） |
| `src/ai_company/` | adapters、work_flow、modules、schemas |
| `.cursor/skills/ai-ceo-framework/` | Cursor 開發本框架的 skill |
| `company_workspace/` | 本機沙盒（`COMPANY_WORKSPACE_ROOT`；含 `_company/`、`projects/<id>/`） |
