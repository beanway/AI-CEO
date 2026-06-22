#!/usr/bin/env bash
# AI Company 本機啟動選單
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3.11 >/dev/null 2>&1; then
  PYTHON="$(command -v python3.11)"
else
  PYTHON="$(command -v python3)"
fi

export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

run_ai_company() {
  echo "啟動 AI Company（雙 Telegram Bot，Ctrl+C 結束）…"
  "$PYTHON" -m ai_company.main run
}

ceo_menu() {
  while true; do
    echo ""
    echo "── CEO 指令 ──"
    echo "  1  初始化工作區 (init-workspace)"
    echo "  2  列出專案 (projects)"
    echo "  3  切換 active 專案 (switch)"
    echo "  4  顯示全公司設定 (global)"
    echo "  b  返回主選單"
    echo ""
    read -r -p "請選擇: " ceo_choice
    case "${ceo_choice}" in
      1)
        "$PYTHON" -m ai_company.ceo_cli init-workspace
        ;;
      2)
        "$PYTHON" -m ai_company.ceo_cli projects
        ;;
      3)
        read -r -p "專案 id: " pid
        if [[ -z "${pid// }" ]]; then
          echo "已取消。"
        else
          "$PYTHON" -m ai_company.ceo_cli switch "$pid"
        fi
        ;;
      4)
        "$PYTHON" -m ai_company.ceo_cli global
        ;;
      b | B)
        return 0
        ;;
      *)
        echo "無效選項，請重試。"
        ;;
    esac
  done
}

main_menu() {
  while true; do
    echo ""
    echo "══ AI Company ══"
    echo "  1  運行 AI Company"
    echo "  2  執行 CEO 指令"
    echo "  q  離開"
    echo ""
    read -r -p "請選擇: " choice
    case "${choice}" in
      1)
        run_ai_company || true
        ;;
      2)
        ceo_menu
        ;;
      q | Q)
        echo "再見。"
        exit 0
        ;;
      *)
        echo "無效選項，請重試。"
        ;;
    esac
  done
}

main_menu
