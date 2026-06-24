#!/usr/bin/env python3
"""第二期驗收模擬（roadmap §十二）：COO 報表、Web dispatch、評分閘道。"""

from __future__ import annotations

import json
import sys
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import simulate_common as sim  # noqa: E402

sim.bootstrap_imports()
sim.register_flows()

from ai_company.adapters.dispatch import dispatch  # noqa: E402
from ai_company.adapters.web.inbound import dispatch_json  # noqa: E402
from ai_company.adapters.web.server import make_handler  # noqa: E402
from ai_company.modules.file_store import core as file_store  # noqa: E402
from ai_company.schemas.commands import CeoChatCommand, ShowCooReportCommand  # noqa: E402


def main() -> int:
    print("第二期（§十二）驗收模擬")
    workspace = sim.temp_workspace("ai-ceo-p2-")
    deps = sim.make_deps(workspace)
    file_store.ensure_company_dirs(workspace)

    chat = dispatch(CeoChatCommand(text="ping"), deps)
    if not chat.success:
        sim.fail("ceo_chat + metrics", chat.message)
        return 1
    sim.ok("ceo_chat 寫入 usage.jsonl")

    report = dispatch(ShowCooReportCommand(), deps)
    if not report.success or not report.total_events:
        sim.fail("COO 報表", report.message)
        return 1
    sim.ok("show_coo_report 報表")

    out = dispatch_json({"command_type": "list_projects"}, deps)
    if not out.get("success"):
        sim.fail("web inbound", str(out))
        return 1
    sim.ok("Web inbound dispatch_json")

    settings = deps.settings
    handler = make_handler(settings, deps)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/v1/dispatch",
            data=json.dumps({"command_type": "show_coo_report"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if not body.get("success"):
            sim.fail("HTTP dispatch", str(body))
            return 1
        sim.ok("HTTP POST /api/v1/dispatch")
    finally:
        server.shutdown()

    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
