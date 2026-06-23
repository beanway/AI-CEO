#!/usr/bin/env python3
"""
Gemini 連線與長文回覆實測（generateContent + Chats API，與 ai_core 相同用法）。

官網要點（2026，google-genai SDK）：
- API Key：環境變數 GEMINI_API_KEY 或 GOOGLE_API_KEY（兩者皆有時 GOOGLE_API_KEY 優先）
- 多輪對話：client.chats.create(model=..., config=...) 後 chat.send_message(...)
- 參數：GenerateContentConfig（system_instruction、max_output_tokens、temperature、thinking_config）
- 關閉 thinking：thinking_config.thinking_budget=0、include_thoughts=False

用法（repo 根目錄）：
  export PYTHONPATH=src
  python scripts/test_gemini_long_reply.py
  python scripts/test_gemini_long_reply.py --model gemini-2.5-flash --min-chars 1200
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from google import genai  # noqa: E402

from ai_company.modules.ai_core import core as ai_core  # noqa: E402
from ai_company.modules.ai_core.core import build_generate_content_config  # noqa: E402
from ai_company.modules.settings.core import (  # noqa: E402
    load_settings,
    resolve_ai_generation,
)
from ai_company.schemas.documents import GlobalConfigFile  # noqa: E402


def _resolve_api_key() -> str:
    return load_settings().resolved_gemini_api_key()


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip("'\"")
        if k and k not in os.environ:
            os.environ[k] = v


def main() -> int:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Gemini 長文回覆實測")
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_TEST_MODEL", "gemini-2.5-flash"),
        help="模型 id（與 global_config.default_model 同格式）",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=8192,
        help="GenerateContentConfig.max_output_tokens",
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=0,
        help="ThinkingConfig.thinking_budget（0 通常表示關閉延伸 thinking）",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=800,
        help="要求模型回覆至少字元數（繁體中文）",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="可選 temperature",
    )
    args = parser.parse_args()

    api_key = _resolve_api_key()
    if not api_key:
        print(
            "錯誤：請設定 GEMINI_API_KEY 或 GOOGLE_API_KEY（官網建議用環境變數，勿寫進 git）",
            file=sys.stderr,
        )
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    system = (
        "你是測試助理。依使用者要求輸出繁體中文，內容要具體、分段清楚，"
        "不要輸出思考過程或 chain-of-thought。"
    )
    user_prompt = (
        f"請用繁體中文寫一篇說明「AI 虛擬公司 Harness 架構」的介紹，"
        f"至少 {args.min_chars} 字，包含 CEO、PM、Worker、沙盒目錄等段落，"
        f"最後用三點條列總結。"
    )

    generation = resolve_ai_generation(
        GlobalConfigFile(
            default_model=args.model,
            max_output_tokens=args.max_output_tokens,
            thinking_budget=args.thinking_budget,
            temperature=args.temperature,
        )
    )
    ai_core.configure_generation(generation)

    config = build_generate_content_config(
        system_instruction=system,
        generation=generation,
    )

    print("── 設定 ──")
    print(f"model: {args.model}")
    print(f"max_output_tokens: {args.max_output_tokens}")
    print(f"thinking_budget: {args.thinking_budget}")
    print(f"api_key_source: {load_settings().resolved_gemini_api_key_source() or '（無）'}")
    print()

    try:
        chat = client.chats.create(model=args.model, config=config)
        response = chat.send_message(user_prompt)
    except Exception as exc:
        print(f"API 呼叫失敗：{exc}", file=sys.stderr)
        print(
            "提示：若 thinking_budget 不支援，可改 --thinking-budget -1 或查官網該模型 thinking 參數。",
            file=sys.stderr,
        )
        return 1

    text = (response.text or "").strip()
    usage = getattr(response, "usage_metadata", None)

    print("── 回覆 ──")
    print(text)
    print()
    print("── 統計 ──")
    print(f"回覆字元數: {len(text)}")
    if usage is not None:
        print(f"usage_metadata: {usage}")
    if len(text) < args.min_chars:
        print(
            f"警告：回覆短於要求（{len(text)} < {args.min_chars}），可提高 max_output_tokens 或換模型。",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
