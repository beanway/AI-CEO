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

pytest_cmd() {
  if [[ -x "$ROOT/.venv/bin/pytest" ]]; then
    echo "$ROOT/.venv/bin/pytest"
  elif command -v pytest >/dev/null 2>&1; then
    command -v pytest
  else
    return 1
  fi
}

run_unit_tests() {
  local pytest_bin
  if ! pytest_bin="$(pytest_cmd)"; then
    echo "找不到 pytest，請在 venv 安裝 dev 依賴：pip install -e '.[dev]'"
    return 1
  fi
  "$pytest_bin" -q
}

run_simulate_p_a3() {
  "$PYTHON" "$ROOT/scripts/simulate_p_a3_acceptance.py"
}

run_all_tests() {
  local ec=0
  echo ""
  echo "▶ 單元測試 (pytest)…"
  if run_unit_tests; then
    echo "  單元測試：PASS"
  else
    echo "  單元測試：FAIL" >&2
    ec=1
  fi
  echo ""
  echo "▶ P-A3 模擬驗收…"
  if run_simulate_p_a3; then
    echo "  模擬驗收：PASS"
  else
    echo "  模擬驗收：FAIL" >&2
    ec=1
  fi
  echo ""
  if [[ "$ec" -eq 0 ]]; then
    echo "全部測試通過。"
  else
    echo "部分測試失敗。" >&2
  fi
  return "$ec"
}

test_menu() {
  while true; do
    echo ""
    echo "── 測試 ──"
    echo "  1  全部（單元測試 + P-A3 模擬驗收）"
    echo "  2  單元測試 (pytest -q)"
    echo "  3  P-A3 模擬驗收 (scripts/simulate_p_a3_acceptance.py)"
    echo "  b  返回主選單"
    echo ""
    read -r -p "請選擇: " test_choice
    case "${test_choice}" in
      1)
        run_all_tests || true
        ;;
      2)
        run_unit_tests || true
        ;;
      3)
        run_simulate_p_a3 || true
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
        "$PYTHON" -m ai_company.adapters.cli init-workspace
        ;;
      2)
        "$PYTHON" -m ai_company.adapters.cli projects
        ;;
      3)
        read -r -p "專案 id: " pid
        if [[ -z "${pid// }" ]]; then
          echo "已取消。"
        else
          "$PYTHON" -m ai_company.adapters.cli switch "$pid"
        fi
        ;;
      4)
        "$PYTHON" -m ai_company.adapters.cli global
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
    echo "  3  測試"
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
      3)
        test_menu
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
