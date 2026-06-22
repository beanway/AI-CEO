# AI 虛擬公司 (AI Company Framework)

Python + Gemini + 雙 Telegram Bot 的 **AI Harness（駕馭層）** 虛擬軟體公司。

**文件（請由此進入）：** [`docs/README.md`](docs/README.md)  
**現行設計：** [`docs/design/harness-design.md`](docs/design/harness-design.md)

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
```

> 注意：`company_workspace` 目錄模型將依 Harness 設計遷移為 `projects/<id>/`；目前程式仍為過渡骨架。

## 目錄

| 路徑 | 說明 |
|------|------|
| `docs/` | 全部產品／設計／路線圖文件 |
| `src/ai_company/` | Router、設定、沙盒（待對齊 Harness） |
| `company_workspace/` | 本機沙盒（待遷移） |
