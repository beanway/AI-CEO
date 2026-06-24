#!/usr/bin/env python3
"""一鍵執行所有 roadmap 模擬驗收腳本（不含 pytest）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = (
    "simulate_p_a1_acceptance.py",
    "simulate_p_a2_acceptance.py",
    "simulate_p_a3_acceptance.py",
    "simulate_p_b_c_acceptance.py",
    "simulate_phase2_acceptance.py",
)


def main() -> int:
    python = sys.executable
    failed: list[str] = []
    print("══ 全部模擬驗收 ══\n")
    for name in SCRIPTS:
        path = ROOT / "scripts" / name
        print(f"▶ {name}")
        proc = subprocess.run([python, str(path)], cwd=ROOT)
        if proc.returncode != 0:
            failed.append(name)
        print()
    if failed:
        print("失敗：" + ", ".join(failed), file=sys.stderr)
        return 1
    print("所有模擬驗收通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
